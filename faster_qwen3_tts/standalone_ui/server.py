"""Local browser studio, inference API, explicit voice library, and ASR proxy."""
from __future__ import annotations

import asyncio
import base64
from contextlib import asynccontextmanager
import io
import json
import logging
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import httpx
import numpy as np
from pydantic import BaseModel, ValidationError
import soundfile as sf

from .gpu import GpuMonitor
from .runtime import GenerationRequest, LANGUAGES, MODELS, SPEAKERS, StudioEngine
from faster_qwen3_tts import __version__

ROOT = Path(__file__).resolve().parent
MAX_UPLOAD = 10 * 1024 * 1024
LOG = logging.getLogger(__name__)


class ModelSelection(BaseModel):
    model: str


def wav_bytes(audio, rate):
    output = io.BytesIO()
    sf.write(output, audio, rate, format='WAV', subtype='PCM_16')
    return output.getvalue()


def create_app(engine=None, data_root: Path | None = None):
    engine = engine or StudioEngine()
    data = data_root or Path(os.getenv('QWEN_STUDIO_DATA', '/app/persistent/studio'))
    voices = data / 'voices'
    voices.mkdir(parents=True, exist_ok=True)
    settings_path = data / 'settings.json'
    settings = {'asr_url': os.getenv('QWEN_STUDIO_ASR_URL', '').strip().rstrip('/')}
    if settings_path.exists():
        settings.update(json.loads(settings_path.read_text(encoding='utf-8')))
    gpu = GpuMonitor()

    @asynccontextmanager
    async def lifespan(app):
        yield
        gpu.close()

    app = FastAPI(title='Faster Qwen3-TTS Studio', version=__version__, lifespan=lifespan,
                  docs_url=None, redoc_url=None)
    app.state.engine = engine
    app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')
    app.mount('/assets', StaticFiles(directory=ROOT / 'assets'), name='assets')

    @app.middleware('http')
    async def no_cache(request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/', include_in_schema=False)
    @app.get('/en', include_in_schema=False)
    def index():
        catalog = json.loads((ROOT / 'static/locales/en.json').read_text(encoding='utf-8'))
        bootstrap = {'locale': 'en', 'defaultLocale': 'en', 'storageKey': 'qwen3tts-ui-locale-v1',
                     'locales': [{'code': 'en', 'name': 'English', 'path': '/en', 'browserLanguage': 'en-US'}],
                     'messages': catalog}
        page = (ROOT / 'static/index.html').read_text(encoding='utf-8')
        page = page.replace('{{UI_VERSION}}', __version__).replace('{{UI_LOCALE}}', 'en').replace('{{UI_DIRECTION}}', 'ltr')
        page = page.replace('{{UI_BOOTSTRAP}}', json.dumps(bootstrap, ensure_ascii=False).replace('<', '\\u003c'))
        return HTMLResponse(page)

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
        return {'models': list(MODELS.values()), 'languages': LANGUAGES, 'speakers': SPEAKERS,
                'modes': ['custom', 'design', 'clone'], 'backend': 'torch', 'streaming': True,
                'formats': ['wav'], 'max_text_chars': 1000, 'max_upload_bytes': MAX_UPLOAD,
                'chunk_size': {'min': 1, 'max': 64, 'default': 8},
                'workflow_defaults': {'custom': {'non_streaming_mode': True},
                                      'design': {'non_streaming_mode': True},
                                      'clone': {'non_streaming_mode': False, 'xvec_only': False}},
                'generation_defaults': GenerationRequest(text='Example').model_dump(exclude={'text'})}

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
        url = str(payload.get('asr_url', '')).strip().rstrip('/')
        if url and not re.match(r'^https?://[^\s]+$', url):
            raise HTTPException(422, 'Enter an HTTP or HTTPS ASR service URL.')
        settings['asr_url'] = url
        temporary = settings_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(settings, indent=2), encoding='utf-8')
        temporary.replace(settings_path)
        return settings

    async def read_audio(upload: UploadFile):
        content = await upload.read(MAX_UPLOAD + 1)
        if not content or len(content) > MAX_UPLOAD:
            raise HTTPException(422, 'Choose an audio file smaller than 10 MB.')
        return content

    def decode_audio(content: bytes):
        try:
            info = sf.info(io.BytesIO(content))
            if info.duration > 120 or info.channels > 2 or info.samplerate > 48000:
                raise ValueError('Decode through the bounded mono conversion path.')
            samples, rate = sf.read(io.BytesIO(content), dtype='float32', always_2d=True)
        except Exception:
            process = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-t', '121',
                                      '-f', 'wav', '-ac', '1', '-ar', '24000', 'pipe:1'],
                                     input=content, capture_output=True, timeout=25)
            if process.returncode:
                raise ValueError('The audio file could not be decoded.')
            samples, rate = sf.read(io.BytesIO(process.stdout), dtype='float32', always_2d=True)
        if not len(samples) or len(samples) / rate > 120 or not np.isfinite(samples).all():
            raise ValueError('Reference audio must contain valid audio up to two minutes long.')
        return wav_bytes(samples.mean(axis=1), rate)

    async def canonical_audio(upload: UploadFile):
        try:
            return await asyncio.to_thread(decode_audio, await read_audio(upload))
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

    def voice_path(voice_id: str):
        if not re.fullmatch(r'[a-f0-9]{32}', voice_id):
            raise HTTPException(404, 'Voice not found.')
        folder = voices / voice_id
        if not folder.is_dir():
            raise HTTPException(404, 'Voice not found.')
        return folder

    @app.get('/studio/voices')
    def voice_list():
        return {'voices': [json.loads(path.read_text(encoding='utf-8'))
                           for path in sorted(voices.glob('*/voice.json'))]}

    @app.post('/studio/voices')
    async def save_voice(name: str = Form(...), transcript: str = Form(''),
                         file: UploadFile = File(...)):
        if not name.strip() or len(name) > 80 or len(transcript) > 4000:
            raise HTTPException(422, 'Provide a voice name up to 80 characters and a transcript up to 4000 characters.')
        audio = await canonical_audio(file)
        voice_id = uuid.uuid4().hex
        folder = voices / voice_id
        folder.mkdir()
        metadata = {'id': voice_id, 'name': name.strip(), 'transcript': transcript,
                    'audio_url': f'/studio/voices/{voice_id}/audio'}
        (folder / 'audio.wav').write_bytes(audio)
        (folder / 'voice.json').write_text(json.dumps(metadata, ensure_ascii=False), encoding='utf-8')
        return metadata

    @app.get('/studio/voices/{voice_id}/audio')
    def voice_audio(voice_id: str):
        return FileResponse(voice_path(voice_id) / 'audio.wav', media_type='audio/wav')

    @app.delete('/studio/voices/{voice_id}')
    def delete_voice(voice_id: str):
        shutil.rmtree(voice_path(voice_id))
        return {'deleted': True}

    async def prepare(options: str, reference: UploadFile | None, voice_id: str):
        try:
            config = GenerationRequest.model_validate_json(options)
        except ValidationError as exc:
            raise HTTPException(422, str(exc)) from exc
        audio = None
        if reference is not None and reference.filename:
            audio = await canonical_audio(reference)
        elif voice_id:
            folder = voice_path(voice_id)
            audio = (folder / 'audio.wav').read_bytes()
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
                emit({'type': 'error', 'message': str(exc)})
            finally:
                emit({'type': 'finished'})

        threading.Thread(target=work, daemon=True, name='qwen-studio-generation').start()
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
                    raise HTTPException(503, event['message'])
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

    return app


def main():
    import uvicorn
    uvicorn.run(create_app(), host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('PORT', '7860')))


if __name__ == '__main__':
    main()
