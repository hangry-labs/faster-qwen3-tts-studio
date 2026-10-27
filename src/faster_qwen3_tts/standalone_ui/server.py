"""Local browser studio, inference API, explicit voice library, and ASR proxy."""
from __future__ import annotations

import asyncio
import base64
from contextlib import asynccontextmanager
import io
import json
import logging
import mimetypes
import os
from pathlib import Path
from functools import lru_cache
import queue
import re
import subprocess
import tempfile
import threading

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
import httpx
import numpy as np
from pydantic import BaseModel, ValidationError
import soundfile as sf

from .gpu import GpuMonitor
from .runtime import GenerationRequest, LANGUAGES, MODELS, SPEAKERS, StudioEngine, start_request_thread
from .profiles import VoiceStore, public_profile
from .model_policy import ModelPolicy
from .reference_inputs import ReferenceInputs
from ..streaming_config import DEFAULT_DECODER_CONTEXT_FRAMES, MAX_DECODER_CONTEXT_FRAMES
from faster_qwen3_tts import __version__

ROOT = Path(__file__).resolve().parent
# Gallery .opus files contain Ogg, rather than raw Opus/RTP packets.
mimetypes.add_type('audio/ogg', '.opus')
GALLERY = Path('/app/examples')
if not GALLERY.is_dir():
    GALLERY = Path(__file__).resolve().parents[3] / 'examples'
MAX_UPLOAD = 10 * 1024 * 1024
LOG = logging.getLogger(__name__)
UI_LOCALES = (
    {'code': 'en', 'name': 'English', 'path': '/en', 'direction': 'ltr', 'browserLanguage': 'en-US'},
    {'code': 'nb', 'name': 'Norsk bokmål', 'path': '/nb', 'direction': 'ltr', 'browserLanguage': 'nb-NO'},
    {'code': 'pl', 'name': 'Polski', 'path': '/pl', 'direction': 'ltr', 'browserLanguage': 'pl-PL'},
    {'code': 'ja', 'name': '日本語', 'path': '/ja', 'direction': 'ltr', 'browserLanguage': 'ja-JP'},
    {'code': 'zh', 'name': '简体中文', 'path': '/zh', 'direction': 'ltr', 'browserLanguage': 'zh-CN'},
    {'code': 'es', 'name': 'Español', 'path': '/es', 'direction': 'ltr', 'browserLanguage': 'es-ES'},
)


@lru_cache(maxsize=len(UI_LOCALES))
def locale_catalog(locale: str) -> dict[str, str]:
    """Merge translated entries over English, including newly introduced keys."""
    catalog = json.loads((ROOT / 'static/locales/en.json').read_text(encoding='utf-8'))
    if locale != 'en':
        translated = json.loads((ROOT / f'static/locales/{locale}.json').read_text(encoding='utf-8'))
        catalog.update({key: value for key, value in translated.items() if isinstance(value, str) and value.strip()})
    return catalog


class ModelSelection(BaseModel):
    model: str


def wav_bytes(audio, rate, subtype='PCM_16'):
    output = io.BytesIO()
    sf.write(output, audio, rate, format='WAV', subtype=subtype)
    return output.getvalue()


def create_app(engine=None, data_root: Path | None = None):
    manage_models = engine is None
    engine = engine or StudioEngine()
    data = data_root or Path(os.getenv('QWEN_STUDIO_DATA', '/app/persistent/studio'))
    voices = data / 'voices'
    voices.mkdir(parents=True, exist_ok=True)
    voice_store = VoiceStore(voices)
    settings_path = data / 'settings.json'
    settings = {'asr_url': os.getenv('QWEN_STUDIO_ASR_URL', '').strip().rstrip('/')}
    for key, variable in [('mcp_enabled', 'QWEN_STUDIO_ENABLE_MCP'), ('mcp_advanced_enabled', 'QWEN_STUDIO_ENABLE_ADVANCED_MCP')]:
        settings[key] = os.getenv(variable, '').lower() in {'1', 'true', 'yes', 'on'}
    if settings_path.exists():
        settings.update(json.loads(settings_path.read_text(encoding='utf-8')))
    settings['model_policy'] = ModelPolicy.model_validate(settings.get('model_policy', {})).model_dump()
    # Injected engines (including isolated benchmark workers) own their loading policy.
    engine.workflow_models = {mode: choice['model'] for mode, choice in settings['model_policy']['workflows'].items()}
    gpu = GpuMonitor()

    @asynccontextmanager
    async def lifespan(app):
        preload = None
        if manage_models:
            preload = asyncio.create_task(asyncio.to_thread(engine.configure_models,
                ModelPolicy.model_validate(settings['model_policy'])))
        try:
            yield
        finally:
            if preload:
                await preload
            gpu.close()

    app = FastAPI(title='Faster Qwen3-TTS Studio', version=__version__, lifespan=lifespan,
                  docs_url=None, redoc_url=None)
    app.state.engine = engine
    app.state.references = ReferenceInputs(data / 'mcp-input')
    app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')
    app.mount('/assets', StaticFiles(directory=ROOT / 'assets'), name='assets')
    if (GALLERY / 'index.html').is_file():
        app.mount('/examples', StaticFiles(directory=GALLERY, html=True), name='examples')

    @app.middleware('http')
    async def no_cache(request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/', include_in_schema=False)
    def index():
        return localized_index('en')

    def localized_index(locale):
        bootstrap = {'locale': locale, 'defaultLocale': 'en', 'storageKey': 'qwen3tts-ui-locale-v1',
                     'locales': UI_LOCALES, 'messages': locale_catalog(locale)}
        page = (ROOT / 'static/index.html').read_text(encoding='utf-8')
        page = page.replace('{{UI_VERSION}}', __version__).replace('{{UI_LOCALE}}', locale).replace('{{UI_DIRECTION}}', 'ltr')
        page = page.replace('{{UI_BOOTSTRAP}}', json.dumps(bootstrap, ensure_ascii=False).replace('<', '\\u003c'))
        return HTMLResponse(page)

    def locale_handler(locale):
        def handler():
            return localized_index(locale)
        return handler

    for locale in UI_LOCALES:
        app.add_api_route(locale['path'], locale_handler(locale['code']), methods=['GET'],
                          include_in_schema=False, name='ui-' + locale['code'])

    @app.get('/favicon.ico', include_in_schema=False)
    def favicon():
        return FileResponse(ROOT / 'assets/qwen3_tts_favicon.webp', media_type='image/webp')

    @app.get('/docs', include_in_schema=False)
    def api_docs():
        return RedirectResponse('/en#api')

    @app.get('/status')
    @app.get('/studio/status')
    def status():
        return engine.status()

    @app.get('/studio/capabilities')
    def capabilities():
        from .live_api import capabilities as live_capabilities
        return {'models': list(MODELS.values()), 'languages': LANGUAGES, 'speakers': SPEAKERS,
                'live_speech': live_capabilities(),
                'modes': ['custom', 'design', 'clone'], 'backend': 'torch', 'streaming': True,
                'formats': ['wav'], 'native_formats': ['wav', 'mp3', 'flac', 'ogg', 'opus', 'aac', 'pcm'],
                'input_types': ['text', 'ssml', 'ssml-h'], 'openai': True, 'magic': True,
                'max_text_chars': 1000, 'max_upload_bytes': MAX_UPLOAD,
                'chunk_size': {'min': 1, 'max': 64, 'default': 8},
                'decoder_context_frames': {'min': 1, 'max': MAX_DECODER_CONTEXT_FRAMES,
                    'default': DEFAULT_DECODER_CONTEXT_FRAMES, 'streaming_only': True},
                'workflow_defaults': {mode: {'non_streaming_mode': mode != 'clone',
                    'model': choice['model'], **({'xvec_only': False} if mode == 'clone' else {})}
                    for mode, choice in settings['model_policy']['workflows'].items()},
                'generation_defaults': GenerationRequest(text='Example', model=engine.workflow_models['custom']).model_dump(exclude={'text'})}

    @app.post('/studio/models/load')
    async def load(selection: ModelSelection):
        if selection.model not in MODELS:
            raise HTTPException(422, 'Unknown model.')
        try:
            return await asyncio.to_thread(engine.load, selection.model)
        except Exception as exc:
            LOG.exception('Model load failed')
            raise HTTPException(503, str(exc)) from exc

    @app.post('/studio/models/unload')
    async def unload():
        return await asyncio.to_thread(engine.unload)

    @app.get('/system/gpu')
    def gpu_status():
        return gpu.request_snapshot()

    @app.get('/system/settings')
    def get_settings():
        return settings

    @app.put('/system/settings')
    async def save_settings(payload: dict):
        access = {}
        for key in ('mcp_enabled', 'mcp_advanced_enabled'):
            if key in payload:
                if not isinstance(payload[key], bool):
                    raise HTTPException(422, 'MCP access settings must be true or false.')
                access[key] = payload[key]
        url = str(payload.get('asr_url', settings['asr_url'])).strip().rstrip('/')
        if url and not re.match(r'^https?://[^\s]+$', url):
            raise HTTPException(422, 'Enter an HTTP or HTTPS ASR service URL.')
        try:
            policy = ModelPolicy.model_validate(payload.get('model_policy', settings['model_policy']))
        except ValidationError as exc:
            raise HTTPException(422, str(exc)) from exc
        settings.update(asr_url=url, model_policy=policy.model_dump(), **access)
        temporary = settings_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(settings, indent=2), encoding='utf-8')
        temporary.replace(settings_path)
        engine.workflow_models = {mode: choice.model for mode, choice in policy.workflows.items()}
        if 'model_policy' in payload and hasattr(engine, 'configure_models'):
            await asyncio.to_thread(engine.configure_models, policy)
        return settings

    async def read_audio(upload: UploadFile):
        content = await upload.read(MAX_UPLOAD + 1)
        if not content or len(content) > MAX_UPLOAD:
            raise HTTPException(422, 'Choose an audio file smaller than 10 MB.')
        return content

    def decode_audio(content: bytes, preserve_float=False):
        try:
            info = sf.info(io.BytesIO(content))
            if info.duration > 120 or info.channels > 2 or info.samplerate > 48000:
                raise ValueError('Decode through the bounded mono conversion path.')
            samples, rate = sf.read(io.BytesIO(content), dtype='float32', always_2d=True)
        except Exception:
            process = subprocess.run(['ffmpeg', '-v', 'error', '-protocol_whitelist', 'pipe', '-i', 'pipe:0', '-t', '121',
                                      '-f', 'wav', '-ac', '1', '-ar', '24000', 'pipe:1'],
                                     input=content, capture_output=True, timeout=25)
            if process.returncode:
                raise ValueError('The audio file could not be decoded.')
            samples, rate = sf.read(io.BytesIO(process.stdout), dtype='float32', always_2d=True)
        if not len(samples) or len(samples) / rate > 120 or not np.isfinite(samples).all():
            raise ValueError('Reference audio must contain valid audio up to two minutes long.')
        return wav_bytes(samples.mean(axis=1), rate, subtype='FLOAT' if preserve_float else 'PCM_16')

    async def canonical_audio(upload: UploadFile, *, preserve_float=False):
        try:
            return await asyncio.to_thread(decode_audio, await read_audio(upload), preserve_float)
        except (ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get('/studio/asr/status')
    async def asr_status():
        if not settings['asr_url']:
            return {'ready': False, 'url': '', 'reason': 'Configure an ASR service URL in System.'}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                result = await client.get(settings['asr_url'] + '/health/ready')
                return {'ready': result.is_success, 'url': settings['asr_url']}
        except httpx.HTTPError:
            return {'ready': False, 'url': settings['asr_url']}

    @app.post('/studio/asr/transcribe')
    async def transcribe(file: UploadFile = File(...)):
        if not settings['asr_url']:
            raise HTTPException(503, 'Configure an ASR service URL in System.')
        audio = await canonical_audio(file)
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                result = await client.post(settings['asr_url'] + '/v1/audio/transcriptions',
                                           files={'file': ('reference.wav', audio, 'audio/wav')},
                                           data={'model': 'qwen3-asr', 'response_format': 'json'})
                result.raise_for_status()
                return {'text': result.json()['text']}
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise HTTPException(503, 'Reference transcription failed. Check the ASR connection in System.') from exc

    @app.get('/studio/voices')
    def voice_list():
        return {'voices': [public_profile(record) for record in voice_store.list()]}

    @app.post('/studio/voices')
    async def save_voice(name: str = Form(...), transcript: str = Form(''),
                         file: UploadFile = File(...)):
        if not name.strip() or len(name) > 80 or len(transcript) > 4000:
            raise HTTPException(422, 'Provide a voice name up to 80 characters and a transcript up to 4000 characters.')
        audio = await canonical_audio(file)
        metadata = voice_store.commit([({'name': name.strip(), 'transcript': transcript}, audio, False)])[name.strip()]
        return public_profile(metadata)

    @app.get('/studio/voices/{voice_id}/audio')
    def voice_audio(voice_id: str):
        try:
            return Response(voice_store.audio(voice_store.resolve(voice_id)), media_type='audio/wav')
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.delete('/studio/voices/{voice_id}')
    def delete_voice(voice_id: str):
        try:
            voice_store.delete(voice_id)
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc
        return {'deleted': True}

    async def prepare(options: str, reference: UploadFile | None, voice_id: str):
        profile = voice_store.resolve(voice_id) if voice_id else None
        try:
            values = json.loads(options)
            if isinstance(values, dict) and 'model' not in values:
                mode = values.get('mode', 'custom')
                if mode in engine.workflow_models:
                    values['model'] = engine.workflow_models[mode]
                    if mode == 'custom' and values.get('instruct') and not MODELS[values['model']]['instructions']:
                        values['model'] = 'Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice'
            if profile and isinstance(values, dict) and not values.get('ref_text'):
                values['ref_text'] = profile.get('transcript', '')
            config = GenerationRequest.model_validate(values)
        except (ValidationError, json.JSONDecodeError) as exc:
            raise HTTPException(422, str(exc)) from exc
        audio = None
        if reference is not None and reference.filename:
            audio = await canonical_audio(reference)
        elif voice_id:
            audio = voice_store.audio(profile)
        if config.mode == 'clone' and audio is None:
            raise HTTPException(422, 'Choose or record reference audio.')
        if config.mode != 'clone' and audio is not None:
            raise HTTPException(422, 'Reference audio belongs to the voice clone workflow.')
        return config, audio

    def start_worker(config, audio, streaming):
        events = queue.Queue(maxsize=16)
        cancelled = threading.Event()

        def emit(event):
            while not cancelled.is_set():
                try:
                    events.put(event, timeout=0.2)
                    return
                except queue.Full:
                    continue

        def work():
            try:
                # Keep references alive until generation has actually stopped, even
                # if an HTTP client disconnects. The engine owns serialization.
                with tempfile.TemporaryDirectory(prefix='qwen-studio-') as temporary:
                    reference_path = None
                    if audio is not None:
                        reference_path = Path(temporary) / 'reference.wav'
                        reference_path.write_bytes(audio)
                    engine.generate(config, reference_path, cancelled, emit, streaming)
            except Exception as exc:
                LOG.exception('Generation failed')
                emit({'type': 'error', 'message': str(exc), 'status_code': getattr(exc, 'status_code', 503)})
            finally:
                emit({'type': 'finished'})

        start_request_thread(engine, work, name='qwen-studio-generation')
        return events, cancelled

    def next_event(events):
        try:
            return events.get(timeout=0.5)
        except queue.Empty:
            return None

    @app.post('/studio/generate/stream')
    async def generate_stream(options: str = Form(...), reference: UploadFile | None = File(None),
                              voice_id: str = Form(''), streaming: bool = True):
        config, audio = await prepare(options, reference, voice_id)
        events, cancelled = start_worker(config, audio, streaming)

        async def stream():
            try:
                while True:
                    event = await asyncio.to_thread(next_event, events)
                    if event is None:
                        yield ': waiting\n\n'
                        continue
                    if event['type'] == 'finished':
                        break
                    if event['type'] == 'chunk':
                        event['audio_b64'] = base64.b64encode(wav_bytes(event.pop('audio'), event['sample_rate'])).decode()
                    yield 'data: ' + json.dumps(event) + '\n\n'
            finally:
                cancelled.set()

        return StreamingResponse(stream(), media_type='text/event-stream',
                                 headers={'X-Accel-Buffering': 'no', 'Cache-Control': 'no-store'})

    @app.post('/studio/generate')
    async def generate(options: str = Form(...), reference: UploadFile | None = File(None),
                       voice_id: str = Form('')):
        config, audio = await prepare(options, reference, voice_id)
        events, cancelled = start_worker(config, audio, False)
        result, metrics, rate = [], {}, 24000
        try:
            while True:
                event = await asyncio.to_thread(next_event, events)
                if event is None:
                    continue
                if event['type'] == 'finished':
                    break
                if event['type'] == 'error':
                    raise HTTPException(event.get('status_code', 503), event['message'])
                if event['type'] == 'chunk':
                    result.append(event['audio'])
                    rate = event['sample_rate']
                if event['type'] == 'done':
                    metrics = event['metrics']
            if not result:
                raise HTTPException(503, 'The model did not produce audio.')
            return {'audio_b64': base64.b64encode(wav_bytes(np.concatenate(result), rate)).decode(),
                    'sample_rate': rate, 'metrics': metrics}
        finally:
            cancelled.set()

    from .api import attach_api
    from .script_api import attach_scripts
    attach_api(app, engine=engine, store=voice_store, canonical_audio=canonical_audio, transcribe=transcribe)
    attach_scripts(app, data / 'scripts')
    from .live_api import attach_live_api
    attach_live_api(app, engine=engine, store=voice_store)
    from .mcp_server import attach_mcp
    attach_mcp(app, data=data, settings=settings)
    return app


def main():
    import uvicorn
    uvicorn.run(create_app(), host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('PORT', '7860')),
                ws_max_size=64*1024, ws_max_queue=4)


if __name__ == '__main__':
    main()
