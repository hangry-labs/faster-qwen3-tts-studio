"""Native and OpenAI-compatible product routes over the shared speech planner."""
from __future__ import annotations

import asyncio
import base64
import hmac
import io
import json
import os
import queue
import threading
import time
import re
from dataclasses import replace
from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import numpy as np
import soundfile as sf

from . import audio
from .magic_takes import MAGIC_TAKE_MEDIA_TYPE, pack_magic_take_bundle
from .openai_voices import attach_openai_voices, voice_object
from .runtime import InferenceQueueFull, LANGUAGES, MODELS, SPEAKERS
from .speech import (CUSTOM, MODEL_ALIASES, NATIVE_LANGUAGES, VOICE_ALIASES,
                     SpeechRequest, SpeechService, capabilities, start_worker)


from ..streaming_config import DEFAULT_DECODER_CONTEXT_FRAMES, MAX_DECODER_CONTEXT_FRAMES


class OpenAISpeechRequest(BaseModel):
    model_config = ConfigDict(extra='ignore', allow_inf_nan=False)
    model: str
    input: str = Field(min_length=1, max_length=4096)
    voice: str | dict[str, str]
    instructions: str | None = Field(default=None, max_length=2000)
    response_format: Literal['mp3', 'opus', 'aac', 'flac', 'wav', 'pcm', 'ogg'] = 'mp3'
    speed: float = Field(default=1, ge=.25, le=4)
    stream_format: Literal['audio'] = 'audio'
    # Explicit Hangry extensions; standard clients omit these.
    language: str = 'English'
    seed: int | None = Field(default=None, ge=0, le=2**32-1)
    voice_profile: str | None = None
    normalize_loudness: bool = False
    protect_long_audio: bool = True
    randomize_seed: bool | None = None
    temperature: float = Field(default=.9, ge=.1, le=2)
    top_k: int = Field(default=50, ge=1, le=200)
    repetition_penalty: float = Field(default=1.05, ge=1, le=2)
    chunk_size: int = Field(default=8, ge=1, le=64)
    decoder_context_frames: int = Field(default=DEFAULT_DECODER_CONTEXT_FRAMES, strict=True,
                                       ge=1, le=MAX_DECODER_CONTEXT_FRAMES)
    max_new_tokens: int = Field(default=360, ge=24, le=600)
    non_streaming_mode: bool | None = None
    xvec_only: bool = False


class MagicTakeRequest(BaseModel):
    payload: SpeechRequest
    speech_index: int = Field(ge=0, lt=64)


class TimelineItem(BaseModel):
    model_config = ConfigDict(extra='forbid', populate_by_name=True)
    kind: Literal['speech', 'break'] = Field(alias='type')
    id: str | None = Field(default=None, max_length=80)
    milliseconds: int = Field(default=0, ge=0, le=10000)


class AssemblyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    items: list[TimelineItem] = Field(min_length=1, max_length=200)
    output_format: Literal['wav', 'mp3', 'flac', 'ogg', 'opus', 'aac', 'pcm'] = 'wav'
    normalize_loudness: bool = False


class EffectsRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    speed: float = Field(default=1, ge=.25, le=4)
    pitch: float = Field(default=0, ge=-12, le=12)
    volume: float = Field(default=1, ge=0, le=2)
    normalize_loudness: bool = False
    output_format: Literal['wav', 'mp3', 'flac', 'ogg', 'opus', 'aac', 'pcm'] = 'wav'
    method: Literal['ffmpeg', 'ffmpeg-shape', 'signalsmith'] = 'ffmpeg'
    preset: Literal['clean', 'studio', 'custom'] = 'custom'
    pitch_semitones: float | None = Field(default=None, ge=-6, le=6)
    speed_factor: float | None = Field(default=None, ge=.75, le=1.25)
    noise_reduction_db: float = Field(default=0, ge=0, le=12)
    bass_db: float = Field(default=0, ge=-6, le=6)
    presence_db: float = Field(default=0, ge=-6, le=6)
    dynamics: float = Field(default=0, ge=0, le=100)
    high_pass_hz: float = Field(default=50, ge=50, le=150)
    warmth_db: float | None = Field(default=None, ge=-4, le=6)
    warmth_hz: float | None = Field(default=None, ge=80, le=250)
    mud_db: float = Field(default=0, ge=-5, le=0)
    mud_hz: float = Field(default=300, ge=180, le=500)
    presence_hz: float | None = Field(default=None, ge=2000, le=5000)
    air_db: float = Field(default=0, ge=-3, le=3)
    air_hz: float = Field(default=10000, ge=7000, le=11000)
    compression_ratio: float | None = Field(default=None, ge=1, le=5)
    compression_attack_ms: float = Field(default=12, ge=3, le=40)
    compression_release_ms: float = Field(default=120, ge=50, le=300)
    compression_threshold_dbfs: float = Field(default=-22, ge=-36, le=-8)
    saturation_blend_percent: float = Field(default=0, ge=0, le=20)
    deesser_strength_percent: float | None = Field(default=None, ge=0, le=100)
    room_percent: float = Field(default=0, ge=0, le=10)
    target_loudness_lufs: float = Field(default=-16, ge=-24, le=-14)
    peak_ceiling_dbtp: float = Field(default=-1.5, ge=-3, le=-.5)


def error_payload(message, status=400, param=None):
    return JSONResponse({'error': {'message': message,
        'type': 'authentication_error' if status == 401 else 'rate_limit_error' if status == 429 else 'invalid_request_error' if status < 500 else 'server_error',
        'param': param, 'code': None}}, status_code=status,
        headers={'WWW-Authenticate': 'Bearer'} if status == 401 else {})


def pop_event(events):
    try:
        return events.get(timeout=.25)
    except queue.Empty:
        return None


def attach_api(app, *, engine, store, canonical_audio, transcribe):
    service = SpeechService(engine, store)
    app.state.speech = service
    router = APIRouter()
    activities = {}
    activity_lock = threading.Lock()

    def begin_activity(request):
        identity = request.headers.get('X-Qwen-Request-ID', '') if request else ''
        if not re.fullmatch(r'[a-zA-Z0-9-]{1,80}', identity):
            return None
        with activity_lock:
            cutoff = time.monotonic() - 3600
            for key in list(activities):
                if activities[key]['updated'] < cutoff:
                    del activities[key]
            if len(activities) >= 128:
                del activities[next(iter(activities))]
            activities[identity] = {'phase': 'queued', 'title': 'Waiting for inference', 'detail': 'Your request is queued', 'updated': time.monotonic()}
        return identity

    def update_activity(identity, event):
        if not identity:
            return
        kind = event['type']
        phases = {
            'queued': ('queued', 'Waiting for inference', 'Your request is queued'),
            'loading': ('loading_model', 'Loading model', 'Preparing Qwen on the GPU'),
            'ready': ('generating', 'Generating speech', 'Qwen is producing your recording'),
            'designing': ('generating', 'Designing a character voice', 'Preparing the dialogue voice'),
            'turn': ('generating', 'Generating dialogue', f"Speech turn {event.get('index', 0) + 1}"),
            'retrying': ('generating', 'Retrying a speech unit', event.get('message', 'Using smaller sections')),
            'chunk': ('streaming', 'Receiving audio', 'Speech is arriving from Qwen'),
            'done': ('encoding', 'Encoding audio', 'Preparing the completed recording'),
            'error': ('failed', 'Generation failed', str(event.get('message', 'Inference failed'))),
            'complete': ('complete', 'Generation complete', 'Recording ready'),
            'cancelled': ('failed', 'Generation stopped', 'The client stopped this request'),
        }
        if kind not in phases:
            return
        phase, title, detail = phases[kind]
        with activity_lock:
            if identity not in activities:
                return
            activities[identity] = {**activities.get(identity, {}), 'phase': phase, 'title': title, 'detail': detail, 'updated': time.monotonic()}
            if kind == 'queued':
                position = event.get('position', 0)
                activities[identity]['queue_position'] = position
                activities[identity]['detail'] = f'{position} request(s) ahead' if position else 'Preparing the selected voice'
            if 'metrics' in event:
                activities[identity]['metrics'] = event['metrics']
            if 'committed_profiles' in event:
                activities[identity]['committed_profiles'] = event['committed_profiles']

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        if request.url.path.startswith('/v1'):
            return error_payload(str(exc), 400)
        return JSONResponse({'detail': str(exc)}, status_code=422)

    @app.exception_handler(ValueError)
    async def value_error(request, exc):
        return error_payload(str(exc)) if request.url.path.startswith('/v1') else JSONResponse({'detail': str(exc)}, status_code=422)

    @app.exception_handler(InferenceQueueFull)
    async def queue_full(request, exc):
        response = error_payload(str(exc), 429) if request.url.path.startswith('/v1') else JSONResponse(
            {'detail': str(exc), 'code': 'inference_queue_full'}, status_code=429)
        response.headers['Retry-After'] = '1'
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        if request.url.path == '/v1' or request.url.path.startswith('/v1/'):
            response = error_payload(str(exc.detail), exc.status_code)
            response.headers.update(exc.headers or {})
            return response
        return JSONResponse({'detail': exc.detail}, status_code=exc.status_code, headers=exc.headers)

    @app.middleware('http')
    async def api_auth(request, call_next):
        if request.url.path == '/v1' or request.url.path.startswith('/v1/'):
            key = os.getenv('QWEN_STUDIO_API_KEY', '').strip()
            scheme, _, provided = request.headers.get('authorization', '').partition(' ')
            if key and (scheme.lower() != 'bearer' or not hmac.compare_digest(provided, key)):
                return error_payload('Incorrect API key provided.', 401)
        return await call_next(request)

    async def complete(prepared, http_request=None, **options):
        identity = begin_activity(http_request)
        events, cancelled = start_worker(service, prepared, **options)
        result = None
        try:
            while True:
                event = await asyncio.to_thread(pop_event, events)
                if http_request is not None and await http_request.is_disconnected():
                    raise HTTPException(499, 'Client disconnected.')
                if event is None:
                    continue
                update_activity(identity, event)
                if event['type'] == 'error':
                    raise HTTPException(event.get('status_code', 503), event['message'])
                if event['type'] == 'result':
                    result = event['result']
                if event['type'] == 'finished':
                    if result is None:
                        raise HTTPException(503, 'Generation ended before completion.')
                    return result
        except (asyncio.CancelledError, HTTPException) as exc:
            if isinstance(exc, asyncio.CancelledError) or exc.status_code == 499:
                update_activity(identity, {'type': 'cancelled'})
            raise
        finally:
            cancelled.set()

    def commit(result):
        records = store.commit(result['pending']) if result['pending'] else {}
        return {name: record['id'] for name, record in records.items()}

    def headers(prepared, fmt):
        return {'X-Qwen-Seed': str(prepared.seed), 'X-Qwen-Sample-Rate': '48000' if fmt == 'opus' else '24000', 'X-Qwen-Format': fmt,
                'X-Qwen-Input-Type': prepared.request.input_type,
                'Content-Disposition': f'inline; filename="qwen3-tts.{fmt}"'}

    async def prepare_generation(payload, reference=None):
        # Reserve before filesystem reads / compilation and retain the same FIFO
        # ticket through CPU finishing. Invalid input and disconnects return it.
        reserve = getattr(service.engine, 'admit', None)
        ticket = reserve() if callable(reserve) else None
        started = time.perf_counter()
        preparation = asyncio.create_task(asyncio.to_thread(service.prepare, payload, reference))
        try:
            prepared = await asyncio.shield(preparation)
            return replace(prepared, admission=ticket, preparation_ms=(time.perf_counter() - started) * 1000)
        except asyncio.CancelledError:
            # A filesystem read cannot be interrupted. Keep its slot until the
            # bounded CPU task actually exits, even if the HTTP task is gone.
            def abandoned(task):
                if ticket is not None:
                    service.engine.cancel_admission(ticket)
                if not task.cancelled():
                    task.exception()
            preparation.add_done_callback(abandoned)
            raise
        except BaseException:
            if ticket is not None:
                service.engine.cancel_admission(ticket)
            raise

    async def binary(payload, http_request=None, reference=None):
        reference = await resolve_reference(payload, reference)
        prepared = await prepare_generation(payload, reference)
        result = await complete(prepared, http_request)
        encoded = await asyncio.to_thread(audio.encode, result['audio'], payload.output_format)
        if http_request is not None and await http_request.is_disconnected():
            raise HTTPException(499, 'Client disconnected before encoding completed.')
        profiles = commit(result)
        update_activity(http_request.headers.get('X-Qwen-Request-ID') if http_request else None, {'type': 'complete'})
        return Response(encoded, media_type=audio.FORMATS[payload.output_format][0],
                        headers={**headers(prepared, payload.output_format), 'X-Qwen-Committed-Profiles': json.dumps(profiles),
                                 'X-Qwen-Metrics': json.dumps(result['metrics'])})

    async def resolve_reference(payload, reference=None):
        if payload.ref_audio:
            if reference is not None or payload.voice_profile:
                raise ValueError('Choose one reference: upload, saved voice or local ref_audio.')
            upload = await app.state.references.read(payload.ref_audio, allow_url=False)
            try:
                return await canonical_audio(upload)
            finally:
                await upload.close()
        return reference

    async def progressive(payload, reference=None, http_request=None):
        prepared = await prepare_generation(payload, reference)
        identity = begin_activity(http_request)
        fmt = payload.stream_format
        events, cancelled = start_worker(service, prepared, streaming=True)
        result = {}
        def chunks():
            while not cancelled.is_set():
                event = pop_event(events)
                if event is None:
                    continue
                kind = event['type']
                update_activity(identity, event)
                if kind == 'chunk':
                    yield event['audio']
                elif kind == 'result':
                    result.update(event['result'])
                elif kind == 'error':
                    raise RuntimeError(event['message'])
                elif kind == 'finished':
                    break
        encoder = audio.encode_stream(chunks(), fmt, cancelled)
        def advance():
            return next(encoder, None)
        async def stream():
            try:
                while (chunk := await asyncio.to_thread(advance)) is not None:
                    yield chunk
                if result and not cancelled.is_set():
                    profiles = commit(result)
                    update_activity(identity, {'type': 'complete', 'metrics': result['metrics'], 'committed_profiles': profiles})
            finally:
                cancelled.set()
                if not result:
                    with activity_lock:
                        phase = activities.get(identity, {}).get('phase')
                    if phase != 'failed':
                        update_activity(identity, {'type': 'cancelled'})
                # Closing happens only after any active next() has returned.
        return StreamingResponse(stream(), media_type=audio.FORMATS[fmt][0], headers=headers(prepared, fmt))

    @router.get('/v1')
    @router.get('/v1/')
    def index():
        return {'object': 'api', 'name': 'Qwen3-TTS Studio',
                'endpoints': ['/v1/models', '/v1/audio/voices', '/v1/audio/voice_consents', '/v1/audio/speech']}

    def model_payload(identity):
        return {'id': identity, 'object': 'model', 'created': 0, 'owned_by': 'qwen',
                'capabilities': MODELS[identity]}

    @router.get('/v1/models')
    def models():
        return {'object': 'list', 'data': [model_payload(m) for m in MODELS]}

    @router.get('/v1/models/{model_id:path}')
    def model(model_id: str):
        if model_id in MODEL_ALIASES:
            return {**model_payload(CUSTOM), 'id': model_id, 'alias_for': 'automatic Qwen voice workflow'}
        if model_id not in MODELS:
            return error_payload('Unknown Qwen model.', 404, 'model')
        return model_payload(model_id)

    @router.get('/v1/audio/voices')
    def openai_voices():
        data = [{'id': s, 'object': 'voice', 'owned_by': 'qwen', 'language': NATIVE_LANGUAGES[s]} for s in SPEAKERS]
        data += [{'id': alias, 'object': 'voice', 'owned_by': 'hangry-labs', 'maps_to': speaker} for alias, speaker in VOICE_ALIASES.items()]
        data += [{**voice_object(v), 'object': 'voice', 'owned_by': 'local'} for v in store.list()]
        return {'object': 'list', 'data': data}

    @router.post('/v1/audio/speech')
    async def openai_speech(payload: OpenAISpeechRequest, request: Request):
        voice = payload.voice.get('id', '').strip() if isinstance(payload.voice, dict) else payload.voice.strip()
        if not voice:
            return error_payload('Custom voice objects need a non-empty id.', param='voice')
        controls = payload.model_dump(exclude={'input', 'voice', 'instructions', 'response_format', 'stream_format'})
        native = SpeechRequest(**controls, text=payload.input, voice=voice,
            instruct=payload.instructions or '', output_format=payload.response_format)
        # Standard OpenAI input is always plain text, including angle brackets.
        try:
            if payload.response_format in {'wav', 'flac'}:
                return await binary(native, request)
            return await progressive(native.model_copy(update={'stream_format': payload.response_format}), http_request=request)
        except HTTPException as exc:
            return error_payload(str(exc.detail), exc.status_code)

    @router.get('/tts/ping')
    def ping():
        from .build_info import build_identity
        return {'msg': 'pong', 'type': 'Qwen3-TTS Studio', **build_identity(), 'backend': 'torch'}

    @router.get('/tts/status')
    def status():
        from .build_info import build_identity
        return {**engine.status(), **build_identity()}

    @router.get('/tts/activity')
    def activity(request_id: str | None = None):
        if request_id is None:
            return engine.status()
        with activity_lock:
            value = activities.get(request_id, {})
            if value and value['updated'] < time.monotonic() - 3600:
                del activities[request_id]
                return {}
            return {key: value[key] for key in ('phase', 'title', 'detail', 'queue_position', 'metrics', 'committed_profiles') if key in value}

    @router.get('/tts/defaults')
    def defaults():
        return SpeechRequest(text='Hello from Hangry Labs Qwen Studio.').model_dump()

    @router.get('/tts/formats')
    def formats():
        return {'default': 'wav', 'formats': {k: {'media_type': v[0], 'extension': k, 'sample_rate': 48000 if k == 'opus' else 24000} for k, v in audio.FORMATS.items()}}

    @router.get('/tts/stream-formats')
    def stream_formats():
        return {'default': 'mp3', 'formats': {k: {'media_type': audio.FORMATS[k][0]} for k in ('mp3', 'pcm', 'opus', 'aac', 'flac', 'ogg')},
                'granularity': {'text': 'codec chunks with bounded internal-edge buffering',
                    'ssml': 'codec chunks per speech unit, preserving planned pauses',
                    'effects': 'one continuous filter per speech unit; normalization once after assembly'}}

    @router.get('/tts/languages')
    def languages():
        return {'languages': LANGUAGES}

    @router.get('/tts/voices')
    @router.get('/tts/speakers')
    def voices():
        return {'voices': [{'id': s, 'name': s, 'language': NATIVE_LANGUAGES[s]} for s in SPEAKERS], 'saved_profiles': profile_list()['data']}

    @router.get('/tts/ssml/capabilities')
    def ssml_capabilities():
        result = capabilities()
        result['ssml_h']['design_processor'].update(model=service.default_model('design'), clone_model=service.default_model('clone'))
        return result

    @router.post('/tts/plan')
    async def plan(payload: SpeechRequest):
        return service.inspect(await asyncio.to_thread(service.prepare, payload, await resolve_reference(payload)))

    @router.post('/tts/metrics')
    async def metrics(payload: SpeechRequest):
        prepared = await asyncio.to_thread(service.prepare, payload, await resolve_reference(payload))
        return {'input_type': payload.input_type, 'metrics': {
            'characters': sum(len(u.text) for u in prepared.plan.units),
            'words': sum(len(u.text.split()) for u in prepared.plan.units),
            'units': len(prepared.plan.units), 'speech_units': sum(u.kind == 'speech' for u in prepared.plan.units),
            'break_ms': sum(u.duration_ms for u in prepared.plan.units),
            'voices': list(prepared.plan.voices), 'languages': list(prepared.plan.languages),
            'voice_definitions': len(prepared.plan.voice_definitions)}}

    @router.post('/tts/generate')
    @router.post('/tts/convert')
    async def generate(payload: SpeechRequest, request: Request):
        return await binary(payload, request)

    @router.post('/tts/generate-upload')
    async def generate_upload(request: Request, payload: str = Form(...), reference_audio: UploadFile = File(...)):
        return await binary(SpeechRequest.model_validate_json(payload), request, await canonical_audio(reference_audio))

    @router.post('/tts/stream')
    async def stream(payload: SpeechRequest, request: Request):
        return await progressive(payload, await resolve_reference(payload), http_request=request)

    @router.post('/tts/stream-upload')
    async def stream_upload(payload: str = Form(...), reference_audio: UploadFile = File(...)):
        parsed = SpeechRequest.model_validate_json(payload)
        return await progressive(parsed, await resolve_reference(parsed, await canonical_audio(reference_audio)))

    @router.post('/tts/events')
    async def events(payload: SpeechRequest):
        prepared = await prepare_generation(payload, await resolve_reference(payload))
        events, cancelled = start_worker(service, prepared, streaming=True)
        async def stream():
            result = None
            try:
                while True:
                    event = await asyncio.to_thread(pop_event, events)
                    if event is None:
                        yield ': waiting\n\n'
                        continue
                    kind = event['type']
                    if kind == 'finished':
                        break
                    if kind == 'result':
                        result = event['result']
                        continue
                    if kind == 'done':
                        continue
                    if kind == 'chunk':
                        event['audio_b64'] = base64.b64encode(audio.wav(event.pop('audio'))).decode()
                    yield 'data: ' + json.dumps(event) + '\n\n'
                    if kind == 'error':
                        return
                if result and not cancelled.is_set():
                    profiles = commit(result)
                    yield 'data: ' + json.dumps({'type': 'done', 'metrics': result['metrics'], 'committed_profiles': profiles}) + '\n\n'
            finally:
                cancelled.set()
        return StreamingResponse(stream(), media_type='text/event-stream', headers={'X-Accel-Buffering': 'no'})

    @router.post('/tts/purge')
    async def purge():
        return await asyncio.to_thread(engine.unload)

    from .profile_api import attach_profiles
    profile_list = attach_profiles(router, store, canonical_audio)
    app.state.voice_consents = attach_openai_voices(router, store, canonical_audio, prepare_generation, complete)

    @router.post('/tts/transcribe-upload')
    async def transcribe_upload(reference_audio: UploadFile = File(...)):
        return await transcribe(reference_audio)

    @router.post('/tts/transcribe')
    async def transcribe_local(payload: dict):
        upload = await app.state.references.read(payload.get('audio_location', payload.get('ref_audio', '')), allow_url=False)
        try:
            return await transcribe(upload)
        finally:
            await upload.close()

    @router.post('/tts/postprocess-upload')
    async def postprocess(options: str = Form(...), audio_file: UploadFile = File(..., alias='audio')):
        from .finishing import finish_audio
        config = EffectsRequest.model_validate_json(options)
        source = await audio_file.read(40 * 1024 * 1024 + 1)
        if not source or len(source) > 40 * 1024 * 1024:
            raise ValueError('Choose generated audio up to 40 MB.')
        converted = await asyncio.to_thread(resample_wav, source)
        waveform = await asyncio.to_thread(finish_audio, converted, config)
        if config.output_format == 'wav':
            output = io.BytesIO()
            sf.write(output, waveform, audio.RATE, format='WAV', subtype='FLOAT')
            encoded = output.getvalue()
        else:
            encoded = await asyncio.to_thread(audio.encode, waveform, config.output_format)
        return Response(encoded, media_type=audio.FORMATS[config.output_format][0])

    async def uploads(files, metadata):
        if not isinstance(metadata, list) or len(metadata) != len(files) or len(files) > 64:
            raise ValueError('Supply one metadata item per take, up to 64 takes.')
        decoded, total = {}, 0
        for file, item in zip(files, metadata):
            identity = item.get('id') if isinstance(item, dict) else None
            if not isinstance(identity, str) or not identity or len(identity) > 80 or identity in decoded:
                raise ValueError('Take ids must be unique, non-empty strings up to 80 characters.')
            content = await file.read(20 * 1024 * 1024 + 1)
            total += len(content)
            if len(content) > 20 * 1024 * 1024 or total > 40 * 1024 * 1024:
                raise ValueError('Take uploads exceed the 20 MB per-file or 40 MB total limit.')
            from .magic_takes import decode_pcm16_mono_wav
            sample_rate, pcm_wave = await asyncio.to_thread(decode_pcm16_mono_wav, content)
            if sample_rate != audio.RATE:
                raise ValueError('Magic takes must use the Qwen output rate, 24000 Hz.')
            waveform = pcm_wave.astype(np.float32) / 32768
            if sum(len(v[1]) for v in decoded.values()) + len(waveform) > audio.RATE * 300:
                raise ValueError('Uploaded takes exceed 300 seconds.')
            seed = item.get('seed', 0)
            if not isinstance(seed, int) or not 0 <= seed < 2**32:
                raise ValueError('Take seed must be an unsigned 32-bit integer.')
            decoded[identity] = (seed, waveform)
        return decoded

    @router.post('/tts/magic/take')
    async def magic_take(payload: MagicTakeRequest, request: Request):
        prepared = await asyncio.to_thread(service.prepare, payload.payload)
        if payload.speech_index >= sum(u.kind == 'speech' for u in prepared.plan.units):
            raise ValueError('Magic speech_index does not identify a speech unit.')
        result = await complete(prepared, request, speech_index=payload.speech_index)
        # Previewing a single turn never commits document-level profiles.
        update_activity(request.headers.get('X-Qwen-Request-ID'), {'type': 'complete'})
        return Response(audio.wav(result['audio']), media_type='audio/wav', headers=headers(prepared, 'wav'))

    @router.post('/tts/magic/render')
    async def magic_render(request: Request, payload: str = Form(...), speech_ids: str = Form(...),
                           retained: str = Form('[]'), takes: list[UploadFile] = File(default=[])):
        config = SpeechRequest.model_validate_json(payload)
        prepared = await asyncio.to_thread(service.prepare, config)
        ids = json.loads(speech_ids)
        count = sum(u.kind == 'speech' for u in prepared.plan.units)
        if not isinstance(ids, list) or len(ids) != count or any(not isinstance(n, str) or not n or len(n) > 80 for n in ids) or len(set(ids)) != len(ids):
            raise ValueError('speech_ids must uniquely identify every compiled speech unit. Shorten turns that split into multiple units.')
        kept = await uploads(takes, json.loads(retained))
        if set(kept) - set(ids):
            raise ValueError('Retained takes must belong to speech_ids.')
        if all(n in kept for n in ids) and prepared.plan.voice_definitions:
            # No need to bootstrap unused dynamic voices just to assemble retained takes.
            prepared = type(prepared)(prepared.request, type(prepared.plan)(prepared.plan.input_type, prepared.plan.units),
                                      prepared.bindings, prepared.seed, prepared.default)
        result = await complete(prepared, request, ids=ids, retained=kept)
        fmt = config.output_format
        encoded = await asyncio.to_thread(audio.encode, result['audio'], fmt)
        encoded_takes = [(n, seed, audio.wav(wave)) for n, (seed, wave) in result['takes'].items()]
        if await request.is_disconnected():
            raise HTTPException(499, 'Client disconnected before encoding completed.')
        profiles = commit(result)
        bundle = pack_magic_take_bundle(encoded_takes,
            encoded, sample_rate=audio.RATE, output_format=fmt, output_media_type=audio.FORMATS[fmt][0],
            request_seed=prepared.seed, committed_profiles=profiles, metrics=result['metrics'])
        update_activity(request.headers.get('X-Qwen-Request-ID'), {'type': 'complete', 'committed_profiles': profiles})
        return Response(bundle, media_type=MAGIC_TAKE_MEDIA_TYPE, headers=headers(prepared, fmt))

    @router.post('/tts/magic/assemble-upload')
    async def magic_assemble(options: str = Form(...), take_metadata: str = Form(...), takes: list[UploadFile] = File(...)):
        config = AssemblyRequest.model_validate_json(options)
        decoded = await uploads(takes, json.loads(take_metadata))
        expected = [item.id for item in config.items if item.kind == 'speech']
        if not expected or any(n not in decoded for n in expected) or set(decoded) != set(expected):
            raise ValueError('Every speech item needs a matching uploaded take; unused takes are rejected.')
        if sum(item.milliseconds for item in config.items if item.kind == 'break') > 60000:
            raise ValueError('Total explicit pauses cannot exceed 60000 ms.')
        waveform = np.concatenate(list(audio.assemble((item.kind, item.milliseconds if item.kind == 'break' else decoded[item.id][1]) for item in config.items)))
        if len(waveform) > audio.RATE * 300:
            raise ValueError('Assembled audio exceeds 300 seconds.')
        if config.normalize_loudness:
            waveform = await asyncio.to_thread(audio.effects, waveform, normalize=True)
        return Response(await asyncio.to_thread(audio.encode, waveform, config.output_format),
                        media_type=audio.FORMATS[config.output_format][0], headers={'X-Qwen-Format': config.output_format})

    app.include_router(router)
    return service


def resample_wav(content):
    """Validate decoded sizes before allocating or handing data to FFmpeg."""
    try:
        info = sf.info(io.BytesIO(content))
        if not 8000 <= info.samplerate <= 48000 or info.channels not in {1, 2} or not 0 < info.duration <= 300:
            raise ValueError('Use audio up to 300 seconds, mono/stereo, 8 to 48 kHz.')
        samples, rate = sf.read(io.BytesIO(content), dtype='float32', always_2d=True)
    except (sf.LibsndfileError, RuntimeError):
        # AAC/ADTS and other generated formats may not have a libsndfile decoder.
        # Decode through the same installed encoder tool, with a hard duration cap.
        import subprocess
        try:
            result = subprocess.run(['ffmpeg', '-v', 'error', '-protocol_whitelist', 'pipe', '-i', 'pipe:0', '-t', '301',
                '-ar', str(audio.RATE), '-ac', '1', '-f', 'f32le', 'pipe:1'],
                input=content, capture_output=True, timeout=60)
        except subprocess.TimeoutExpired as exc:
            raise ValueError('Audio decoding timed out.') from exc
        if result.returncode or not result.stdout:
            raise ValueError('Upload valid audio in a supported format.')
        samples = np.frombuffer(result.stdout, dtype='<f4').copy()
        if len(samples) > audio.RATE * 300 or not np.isfinite(samples).all():
            raise ValueError('Audio must contain finite samples and last no more than 300 seconds.')
        return samples
    if not np.isfinite(samples).all():
        raise ValueError('Audio contains non-finite samples.')
    samples = samples.mean(axis=1)
    if rate != audio.RATE:
        import subprocess
        result = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(rate), '-ac', '1',
            '-i', 'pipe:0', '-ar', str(audio.RATE), '-f', 'f32le', 'pipe:1'],
            input=samples.astype('<f4').tobytes(), capture_output=True, timeout=60)
        if result.returncode:
            raise ValueError('Audio resampling failed.')
        samples = np.frombuffer(result.stdout, dtype='<f4').copy()
    return samples
