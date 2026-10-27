# SPDX-License-Identifier: MIT AND Apache-2.0
"""One bounded text-in/audio-out utterance per native WebSocket connection."""
from __future__ import annotations

import asyncio
import io
import json
import logging
from pathlib import Path
import queue
import secrets
import tempfile
import threading
import time
from typing import Literal
from urllib.parse import urlsplit

from anyio import CancelScope
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, ValidationError
import soundfile as sf

from ..live_input import LIVE_MODEL, TextInput, validate_live_model
from ..streaming_config import DEFAULT_DECODER_CONTEXT_FRAMES, MAX_DECODER_CONTEXT_FRAMES
from .runtime import GenerationIncomplete, GenerationRequest, InferenceQueueFull, start_request_thread

LOG = logging.getLogger(__name__)
MAX_MESSAGE_BYTES = 32 * 1024
MAX_INPUT_CHARS = 4000
MAX_INPUT_TOKENS = 1500
MAX_SESSION_SECONDS = 120
MAX_CONNECTION_SECONDS = MAX_SESSION_SECONDS+60
SEND_TIMEOUT = 10.
OUTPUT_CHUNKS = 8


class LiveStart(BaseModel):
    type: Literal['start']
    voice: str = Field(min_length=1, max_length=256)
    model: str | None = None
    mode: Literal['clone'] = 'clone'
    input_type: Literal['text'] = 'text'
    response_format: Literal['pcm'] = 'pcm'
    non_streaming_mode: Literal[False] = False
    text: str = Field(default='', max_length=MAX_INPUT_CHARS)
    language: str = 'English'
    ref_text: str | None = Field(default=None, max_length=4000)
    xvec_only: bool = False
    instruct: str = Field(default='', max_length=2000)
    seed: int | None = Field(default=None, ge=0, le=4294967295)
    temperature: float = Field(default=.9, ge=.1, le=2)
    top_k: int = Field(default=50, ge=1, le=200)
    repetition_penalty: float = Field(default=1.05, ge=1, le=2)
    max_new_tokens: int = Field(default=600, ge=24, le=600)
    chunk_size: int = Field(default=8, ge=1, le=64)
    decoder_context_frames: int = Field(default=DEFAULT_DECODER_CONTEXT_FRAMES, strict=True,
                                       ge=1, le=MAX_DECODER_CONTEXT_FRAMES)
    input_timeout_s: float = Field(default=15., ge=1, le=60)


def capabilities():
    return {'path': '/tts/live', 'transport': 'websocket', 'version': 1,
            'workflow': 'clone', 'models': [LIVE_MODEL], 'default_model': LIVE_MODEL,
            'cloning_modes': {'icl': {'xvec_only': False}, 'speaker_only': {'xvec_only': True}},
            'input_type': 'text', 'format': 'pcm_s16le',
            'sample_rate': 24000, 'channels': 1, 'utterances_per_connection': 1,
            'max_input_chars': MAX_INPUT_CHARS, 'max_input_tokens': MAX_INPUT_TOKENS,
            'max_session_seconds': MAX_SESSION_SECONDS, 'max_connection_seconds': MAX_CONNECTION_SECONDS}


async def receive_message(socket):
    message = await socket.receive()
    if message['type'] == 'websocket.disconnect':
        raise WebSocketDisconnect(message.get('code', 1000))
    text = message.get('text')
    if not isinstance(text, str):
        raise ValueError('Send JSON text messages; audio is returned as binary PCM.')
    if len(text.encode('utf-8')) > MAX_MESSAGE_BYTES:
        raise ValueError('Live messages must be no larger than 32 KiB.')
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError('A live message must be a JSON object.')
    return value


def attach_live_api(app, *, engine, store):
    @app.websocket('/tts/live')
    async def live(socket: WebSocket):
        origin = socket.headers.get('origin')
        if origin and (urlsplit(origin).scheme not in {'http', 'https'} or
                       urlsplit(origin).netloc.lower() != socket.headers.get('host', '').lower()):
            await socket.close(code=1008)
            return
        await socket.accept()
        feed = None
        worker = None
        ticket = None
        tasks = []
        disconnected = threading.Event()
        failure = {}
        events = queue.Queue(maxsize=OUTPUT_CHUNKS)

        def emit(event):
            if event['type'] == 'chunk':
                output = io.BytesIO()
                sf.write(output, event['audio'], 24000, format='RAW', subtype='PCM_16', endian='LITTLE')
                event = {'type': 'audio', 'pcm': output.getvalue()}
            deadline = time.monotonic()+SEND_TIMEOUT
            while not disconnected.is_set():
                try:
                    events.put(event, timeout=.1)
                    return
                except queue.Full:
                    if time.monotonic() >= deadline:
                        feed.cancel()
                        raise TimeoutError('Live audio consumer stopped reading.')
            raise InterruptedError('Live connection closed.')

        try:
            try:
                payload = await asyncio.wait_for(receive_message(socket), 10.)
                start = LiveStart.model_validate(payload)
                with store.lock:
                    voice = store.resolve(start.voice)
                    reference = store.audio(voice)
                    transcript = voice.get('transcript', '') if start.ref_text is None else start.ref_text
                if not reference or len(reference) > 10*1024*1024:
                    raise ValueError('Choose a saved reference smaller than 10 MB.')
                model = LIVE_MODEL if start.model is None else start.model
                validate_live_model(model)
                request = GenerationRequest(**start.model_dump(exclude={
                    'type', 'voice', 'ref_text', 'text', 'model', 'seed', 'input_type', 'response_format', 'input_timeout_s'}),
                    text='Live speech', model=model, ref_text=transcript,
                    seed=start.seed if start.seed is not None else secrets.randbits(32))
            except (ValueError, ValidationError, OSError, asyncio.TimeoutError) as exc:
                message = ('Send a start message within 10 seconds.' if isinstance(exc, asyncio.TimeoutError) else
                           'Saved reference audio is unavailable. Restore or replace the voice.' if isinstance(exc, OSError) else str(exc))
                await socket.send_json({'type': 'error', 'code': 'invalid_request', 'message': message})
                await socket.close(code=1008)
                return
            feed = TextInput(idle_timeout=start.input_timeout_s, max_seconds=MAX_SESSION_SECONDS,
                             max_chars=MAX_INPUT_CHARS, max_tokens=MAX_INPUT_TOKENS)
            feed.append(start.text)
            try:
                ticket = engine.admit()
            except InferenceQueueFull as exc:
                await socket.send_json({'type': 'error', 'code': 'queue_full', 'message': str(exc)})
                await socket.close(code=1013)
                return
            await socket.send_json({'type': 'accepted', 'version': 1, 'voice': voice['id'],
                'model': model, 'seed': request.seed, 'xvec_only': request.xvec_only,
                'format': 'pcm_s16le', 'sample_rate': 24000, 'channels': 1})

            def work():
                def terminal(event):
                    if disconnected.is_set():
                        return
                    try:
                        emit(event)
                    except (InterruptedError, TimeoutError):
                        disconnected.set()
                        feed.cancel()
                try:
                    with tempfile.TemporaryDirectory(prefix='qwen-live-') as temporary:
                        path = Path(temporary)/'reference.wav'
                        path.write_bytes(reference)
                        engine.generate_live(request, path, feed, emit)
                except InterruptedError:
                    if failure:
                        terminal({'type': 'error', **failure})
                    else:
                        terminal({'type': 'cancelled'})
                except (ValueError, TimeoutError, GenerationIncomplete) as exc:
                    event = {'type': 'error', 'code': 'input_timeout' if isinstance(exc, TimeoutError) else
                             'incomplete' if isinstance(exc, GenerationIncomplete) else 'invalid_input', 'message': str(exc)}
                    if isinstance(exc, GenerationIncomplete):
                        event['metrics'] = exc.metrics
                    terminal(event)
                except Exception:
                    LOG.exception('Live speech generation failed')
                    terminal({'type': 'error', 'code': 'generation_failed', 'message': 'Live speech failed. Check the server logs.'})
                finally:
                    terminal({'type': '_finished'})

            worker = start_request_thread(engine, work, name='qwen-live-generation', ticket=ticket)

            async def receiver():
                try:
                    while True:
                        payload = await receive_message(socket)
                        kind = payload.get('type')
                        if kind == 'text':
                            feed.append(payload.get('text'))
                        elif kind == 'finish':
                            feed.finish()
                        elif kind == 'cancel':
                            feed.cancel()
                        else:
                            raise ValueError('After start, send text, finish or cancel messages.')
                except WebSocketDisconnect:
                    disconnected.set()
                    feed.cancel()
                except InterruptedError:
                    await asyncio.Future()
                except (ValueError, TimeoutError) as exc:
                    failure.update(code='invalid_input', message=str(exc))
                    feed.cancel()
                    # Let the single writer deliver the terminal error.
                    await asyncio.Future()

            def next_event():
                try:
                    return events.get(timeout=.1)
                except queue.Empty:
                    return None

            async def sender():
                while True:
                    event = await asyncio.to_thread(next_event)
                    if event is None:
                        continue
                    if event['type'] == '_finished':
                        await socket.close(code=1000)
                        return
                    if event['type'] == 'audio':
                        await asyncio.wait_for(socket.send_bytes(event['pcm']), SEND_TIMEOUT)
                    else:
                        await asyncio.wait_for(socket.send_json(event), SEND_TIMEOUT)

            tasks = [asyncio.create_task(receiver()), asyncio.create_task(sender())]
            done, _ = await asyncio.wait(tasks, timeout=MAX_CONNECTION_SECONDS, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        except (WebSocketDisconnect, RuntimeError, asyncio.TimeoutError):
            pass
        finally:
            disconnected.set()
            if feed is not None:
                feed.cancel()
            for task in tasks:
                task.cancel()
            # ASGI cancellation can arrive again at every await. Finish cleanup
            # before allowing the enclosing request's cancellation to propagate.
            with CancelScope(shield=True):
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                if worker is not None:
                    await asyncio.to_thread(worker.join, 10.)
                elif ticket is not None:
                    engine.cancel_admission(ticket)
                try:
                    await socket.close(code=1000)
                except (RuntimeError, WebSocketDisconnect):
                    pass
