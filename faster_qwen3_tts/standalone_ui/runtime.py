"""Serialized NVIDIA inference, model capabilities, and request validation."""
from __future__ import annotations

import gc
import threading
import time
from collections import deque
from pathlib import Path
from typing import Callable, Literal

import numpy as np
from pydantic import BaseModel, Field, model_validator


LANGUAGES = ['Auto', 'Chinese', 'English', 'Japanese', 'Korean', 'German', 'French',
             'Russian', 'Portuguese', 'Spanish', 'Italian']
SPEAKERS = ['Vivian', 'Serena', 'Uncle_Fu', 'Dylan', 'Eric', 'Ryan', 'Aiden', 'Ono_Anna', 'Sohee']
_REVISIONS = {
    '0.6B-Base': '5d83992436eae1d760afd27aff78a71d676296fc',
    '1.7B-Base': 'fd4b254389122332181a7c3db7f27e918eec64e3',
    '0.6B-CustomVoice': '85e237c12c027371202489a0ec509ded67b5e4b5',
    '1.7B-CustomVoice': '0c0e3051f131929182e2c023b9537f8b1c68adfe',
    '1.7B-VoiceDesign': '5ecdb67327fd37bb2e042aab12ff7391903235d3',
}
MODELS = {
    f'Qwen/Qwen3-TTS-12Hz-{name}': {
        'id': f'Qwen/Qwen3-TTS-12Hz-{name}', 'label': name, 'revision': revision,
        'mode': 'clone' if name.endswith('Base') else 'design' if name.endswith('VoiceDesign') else 'custom',
        'instructions': name.endswith('Base') or name.startswith('1.7B'),
        'instruction_support': 'experimental' if name.endswith('Base') else 'supported' if name.startswith('1.7B') else 'none',
        'license': 'Apache-2.0',
    } for name, revision in _REVISIONS.items()
}


class GenerationRequest(BaseModel):
    mode: Literal['custom', 'design', 'clone'] = 'custom'
    model: str = 'Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice'
    text: str = Field(min_length=1, max_length=1000)
    language: str = 'English'
    speaker: str = 'Ryan'
    instruct: str = Field(default='', max_length=1500)
    ref_text: str = Field(default='', max_length=4000)
    xvec_only: bool = False
    non_streaming_mode: bool | None = None
    temperature: float = Field(default=0.9, ge=0.1, le=2)
    top_k: int = Field(default=50, ge=1, le=200)
    repetition_penalty: float = Field(default=1.05, ge=1, le=2)
    chunk_size: int = Field(default=8, ge=1, le=64)
    max_new_tokens: int = Field(default=360, ge=24, le=600)
    seed: int | None = Field(default=None, ge=0, le=4294967295)

    @model_validator(mode='after')
    def validate_capabilities(self):
        spec = MODELS.get(self.model)
        if spec is None or spec['mode'] != self.mode:
            raise ValueError('Choose a model for the selected voice workflow.')
        if not self.text.strip():
            raise ValueError('Enter some text to speak.')
        if self.language not in LANGUAGES:
            raise ValueError('Choose a supported language.')
        if self.mode == 'custom' and self.speaker not in SPEAKERS:
            raise ValueError('Choose a supported custom speaker.')
        if self.mode == 'design' and not self.instruct.strip():
            raise ValueError('Describe the voice you want to design.')
        if self.instruct.strip() and not spec['instructions']:
            raise ValueError('Voice instructions require a Base, 1.7B CustomVoice or VoiceDesign model.')
        if self.mode == 'clone' and not self.xvec_only and not self.ref_text.strip():
            raise ValueError('Transcript-guided cloning requires the exact reference transcript.')
        if self.non_streaming_mode is None:
            self.non_streaming_mode = self.mode != 'clone'
        return self


class StudioEngine:
    def __init__(self):
        self.gate = threading.Lock()
        self.state_lock = threading.Lock()
        self.model = None
        self.model_id: str | None = None
        self.state = 'idle'
        self.error: str | None = None
        self.queued = 0
        self.waiters = deque()

    def status(self):
        with self.state_lock:
            return {'state': self.state, 'model': self.model_id, 'loaded': self.model is not None,
                    'error': self.error, 'queue_depth': self.queued, 'backend': 'torch',
                    'default_backend': 'torch', 'available_backends': ['torch']}

    def _state(self, state: str, error: str | None = None):
        with self.state_lock:
            self.state, self.error = state, error

    def _acquire(self, cancelled: threading.Event, emit):
        ticket = object()
        with self.state_lock:
            self.waiters.append(ticket)
            self.queued = len(self.waiters)
            position = len(self.waiters) - 1 + int(self.gate.locked())
        try:
            emit({'type': 'queued', 'position': position})
            while not cancelled.is_set():
                with self.state_lock:
                    current = self.waiters.index(ticket) + int(self.gate.locked())
                    acquired = self.waiters[0] is ticket and self.gate.acquire(blocking=False)
                    if acquired:
                        self.waiters.popleft()
                        self.queued = len(self.waiters)
                if acquired:
                    return True
                if current != position:
                    emit({'type': 'queued', 'position': current})
                    position = current
                cancelled.wait(0.1)
            return False
        finally:
            with self.state_lock:
                if ticket in self.waiters:
                    self.waiters.remove(ticket)
                self.queued = len(self.waiters)

    def _unload(self):
        import torch
        if hasattr(self.model, 'clear_voice_prompt_cache'):
            self.model.clear_voice_prompt_cache()
        self.model = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self.model_id = None

    def _load(self, model_id: str):
        if model_id not in MODELS:
            raise ValueError('Unknown model.')
        if self.model_id == model_id and self.model is not None:
            return
        from huggingface_hub import snapshot_download
        from faster_qwen3_tts import FasterQwen3TTS
        self._state('loading')
        self._unload()
        spec = MODELS[model_id]
        path = snapshot_download(model_id, revision=spec['revision'])
        self.model = FasterQwen3TTS.from_pretrained(path, backend='torch', max_seq_len=2048)
        self.model.warmup(prefill_len=100)
        self.model_id = model_id
        self._state('ready')

    def load(self, model_id: str):
        with self.gate:
            try:
                self._load(model_id)
            except Exception as exc:
                self._unload()
                self._state('error', str(exc))
                raise
        return self.status()

    def unload(self):
        with self.gate:
            self._unload()
            self._state('idle')
        return self.status()

    def generate(self, request: GenerationRequest, reference: Path | None,
                 cancelled: threading.Event, emit: Callable[[dict], None], streaming: bool):
        started = time.perf_counter()
        if not self._acquire(cancelled, emit):
            return
        queue_ms = (time.perf_counter() - started) * 1000
        try:
            if cancelled.is_set():
                return
            load_started = time.perf_counter()
            if self.model_id != request.model or self.model is None:
                emit({'type': 'loading', 'model': request.model})
            self._load(request.model)
            model_load_ms = (time.perf_counter() - load_started) * 1000
            if cancelled.is_set():
                return
            import torch
            if request.seed is not None:
                torch.manual_seed(request.seed)
                torch.cuda.manual_seed_all(request.seed)
            self._state('generating')
            emit({'type': 'ready', 'model': request.model})
            kwargs = {name: getattr(request, name) for name in (
                'text', 'language', 'non_streaming_mode', 'temperature', 'top_k',
                'repetition_penalty', 'max_new_tokens')}
            if request.mode == 'clone':
                if reference is None:
                    raise ValueError('Upload or record reference audio for cloning.')
                kwargs.update(ref_audio=str(reference), ref_text=request.ref_text, xvec_only=request.xvec_only,
                              instruct=request.instruct)
                method = 'generate_voice_clone'
            elif request.mode == 'custom':
                kwargs.update(speaker=request.speaker, instruct=request.instruct)
                method = 'generate_custom_voice'
            else:
                kwargs.update(instruct=request.instruct)
                method = 'generate_voice_design'
            generation_start = time.perf_counter()
            rate = 24000
            model_first_ms, model_generation_ms = None, None

            def metrics(elapsed, duration, first_audio_ms):
                return {'generation_ms': round(elapsed * 1000),
                        'total_ms': round((time.perf_counter() - started) * 1000),
                        'queue_ms': round(queue_ms), 'model_load_ms': round(model_load_ms),
                        'ttfa_ms': round(first_audio_ms or 0), 'duration_s': round(duration, 3),
                        'speed': round(duration / elapsed, 3) if elapsed else 0,
                        'model_ttfa_ms': round(model_first_ms) if model_first_ms is not None else None,
                        'model_generation_ms': round(model_generation_ms) if model_generation_ms is not None else None,
                        'reference_preparation_ms': getattr(self.model, 'last_reference_preparation_ms', None) if request.mode == 'clone' else None,
                        'reference_cache_hit': getattr(self.model, 'last_reference_cache_hit', None) if request.mode == 'clone' else None}

            if streaming:
                kwargs['chunk_size'] = request.chunk_size
                generator = getattr(self.model, method + '_streaming')(**kwargs)
                first_audio_ms = None
                duration = 0.0
                try:
                    for audio, rate, timing in generator:
                        if cancelled.is_set():
                            break
                        audio = flatten_audio(audio)
                        if not len(audio):
                            continue
                        if 'prefill_ms' in timing or 'decode_ms' in timing:
                            model_generation_ms = (model_generation_ms or 0) + timing.get('prefill_ms', 0) + timing.get('decode_ms', 0)
                        if first_audio_ms is None:
                            first_audio_ms = (time.perf_counter() - generation_start) * 1000
                            model_first_ms = model_generation_ms
                        duration += len(audio) / rate
                        emit({'type': 'chunk', 'audio': audio, 'sample_rate': rate,
                              'ttfa_ms': first_audio_ms, 'duration_s': duration,
                              'metrics': metrics(time.perf_counter() - generation_start, duration, first_audio_ms)})
                finally:
                    generator.close()
                elapsed = time.perf_counter() - generation_start
            else:
                audio, rate = getattr(self.model, method)(**kwargs)
                audio = flatten_audio(audio)
                elapsed = time.perf_counter() - generation_start
                duration = len(audio) / rate
                first_audio_ms = elapsed * 1000
                if not cancelled.is_set():
                    emit({'type': 'chunk', 'audio': audio, 'sample_rate': rate,
                          'ttfa_ms': first_audio_ms, 'duration_s': duration})
            if not cancelled.is_set() and duration <= 0:
                raise RuntimeError('The model did not produce audio. Try another text or reference.')
            if not cancelled.is_set():
                emit({'type': 'done', 'model': request.model, 'sample_rate': rate,
                      'metrics': metrics(elapsed, duration, first_audio_ms)})
            self._state('ready')
        except Exception as exc:
            self._state('error', str(exc))
            raise
        finally:
            self.gate.release()


def flatten_audio(audio):
    if isinstance(audio, list):
        return np.concatenate([np.asarray(part).reshape(-1) for part in audio]).astype(np.float32)
    return np.asarray(audio, dtype=np.float32).reshape(-1)
