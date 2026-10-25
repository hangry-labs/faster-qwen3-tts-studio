"""Serialized NVIDIA inference, model capabilities, and request validation."""
from __future__ import annotations

import gc
import os
import sys
import threading
import time
from contextlib import contextmanager
from collections import deque
from pathlib import Path
from typing import Callable, Literal

import numpy as np
from pydantic import BaseModel, Field, model_validator

from .model_catalog import MODELS


LANGUAGES = ['Auto', 'Chinese', 'English', 'Japanese', 'Korean', 'German', 'French',
             'Russian', 'Portuguese', 'Spanish', 'Italian']
SPEAKERS = ['Vivian', 'Serena', 'Uncle_Fu', 'Dylan', 'Eric', 'Ryan', 'Aiden', 'Ono_Anna', 'Sohee']


class InferenceQueueFull(RuntimeError):
    """Admission failed before a worker or response stream was started."""


class GenerationIncomplete(RuntimeError):
    status_code = 422

    def __init__(self, reason, metrics):
        super().__init__('Speech reached the ' + reason + ' generation limit before the model ended. '
                         'Use shorter speech units or increase Maximum audio length.')
        self.reason, self.metrics = reason, metrics


def start_request_thread(engine, work, *, name, ticket=None):
    """Reserve bounded capacity synchronously, before HTTP streaming headers."""
    reserve = getattr(engine, 'admit', None)
    ticket = reserve() if ticket is None and callable(reserve) else ticket

    def run():
        if ticket is None:
            work()
        else:
            with engine.admitted(ticket):
                work()

    thread = threading.Thread(target=run, daemon=True, name=name)
    try:
        thread.start()
    except BaseException:
        if ticket is not None:
            engine.cancel_admission(ticket)
        raise
    return thread


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
    def __init__(self, *, queue_capacity=None):
        value = os.getenv('QWEN_STUDIO_QUEUE_SIZE', '8') if queue_capacity is None else queue_capacity
        try:
            valid = not isinstance(value, bool) and str(value) == str(int(value)) and 0 <= int(value) <= 256
        except (TypeError, ValueError, OverflowError):
            valid = False
        if not valid:
            raise ValueError('QWEN_STUDIO_QUEUE_SIZE must be an integer from 0 to 256.')
        self.queue_capacity = int(value)
        self.queue_rejected = 0
        self.gate = threading.Lock()
        self.state_lock = threading.Lock()
        self.model = None
        self.model_id: str | None = None
        self.state = 'idle'
        self.error: str | None = None
        self.queued = 0
        self.waiters = deque()
        self.admissions = set()
        self.session_owner = threading.local()
        self.models = {}
        self.policy = None
        self.residency_errors = {}

    @contextmanager
    def session(self, cancelled, emit):
        """Keep one FIFO GPU lease across all voices and bootstrap samples."""
        acquired = self._acquire(cancelled, emit)
        if not acquired:
            raise InterruptedError('Generation cancelled.')
        self.session_owner.active = True
        try:
            yield
        finally:
            self.session_owner.active = False
            try:
                self._release_transient()
            finally:
                self.gate.release()

    def status(self):
        torch = sys.modules.get('torch')
        cuda = getattr(torch, 'cuda', None)
        memory = None
        if cuda is not None and cuda.is_initialized():
            memory = {'allocated_mib': round(cuda.memory_allocated() / 1024**2, 2),
                      'reserved_mib': round(cuda.memory_reserved() / 1024**2, 2)}
        with self.state_lock:
            return {'state': self.state, 'model': self.model_id, 'loaded': self.model is not None,
                    'error': self.error, 'queue_depth': self.queued, 'backend': 'torch',
                    'default_backend': 'torch', 'available_backends': ['torch'],
                    'resident_models': list(self.models),
                    'requested_resident_models': sorted(self.policy.resident_models) if self.policy else [],
                    'residency_errors': dict(self.residency_errors), 'gpu_memory': memory,
                    'queue': {'workers': 1, 'capacity': self.queue_capacity,
                              'active': int(self.gate.locked()), 'queued': self.queued,
                              'inflight': len(self.admissions),
                              'rejected': self.queue_rejected}}

    def configure_models(self, policy):
        """Apply under the same lease as inference. Never evict pinned weights to hide OOM."""
        with self.gate:
            self.policy = policy
            self.residency_errors = {}
            self._release_transient()
            for model_id in sorted(policy.resident_models):
                try:
                    self._load(model_id)
                except Exception as exc:
                    self.residency_errors[model_id] = str(exc)
                    self._discard(model_id)
            if self.residency_errors:
                self._state('error', 'Some resident models could not load. Free GPU memory or change residency settings.')
            else:
                self._state('ready' if self.models else 'idle')
        return self.status()

    def _release_transient(self):
        if self.policy is not None:
            for model_id in list(self.models):
                if model_id not in self.policy.resident_models:
                    self._discard(model_id)
            if self.state != 'error':
                self._state('ready' if self.models else 'idle')

    def _discard(self, model_id):
        model = self.models.pop(model_id, None)
        self._dispose(model)
        if self.model_id == model_id:
            self.model_id, self.model = next(iter(self.models.items()), (None, None))
        del model
        self._trim_cuda()

    def _state(self, state: str, error: str | None = None):
        with self.state_lock:
            self.state, self.error = state, error

    def admit(self):
        """Bound the complete synthesis pipeline, including CPU finishing."""
        ticket = object()
        with self.state_lock:
            slots = self.queue_capacity + int(not self.gate.locked())
            if len(self.admissions) >= self.queue_capacity + 1 or len(self.waiters) >= slots:
                self.queue_rejected += 1
                raise InferenceQueueFull('Inference queue is full. Retry after a running request finishes.')
            self.waiters.append(ticket)
            self.admissions.add(ticket)
            self.queued = len(self.waiters)
        return ticket

    def cancel_admission(self, ticket, *, waiting_only=False):
        with self.state_lock:
            if ticket in self.waiters:
                self.waiters.remove(ticket)
            if not waiting_only:
                self.admissions.discard(ticket)
            self.queued = len(self.waiters)

    @contextmanager
    def admitted(self, ticket):
        self.session_owner.admission = ticket
        try:
            yield
        finally:
            self.session_owner.admission = None
            self.cancel_admission(ticket)

    def _acquire(self, cancelled: threading.Event, emit):
        if cancelled.is_set():
            return False
        ticket = getattr(self.session_owner, 'admission', None)
        managed = ticket is not None
        self.session_owner.admission = None
        if ticket is None:
            ticket = self.admit()
        with self.state_lock:
            position = self.waiters.index(ticket) + int(self.gate.locked())
        acquired = False
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
            self.cancel_admission(ticket, waiting_only=acquired and managed)

    def _unload(self):
        removed = list(self.models.values())
        if self.model is not None and not any(model is self.model for model in removed):
            removed.append(self.model)
        self.model = None
        self.models.clear()
        while removed:
            self._dispose(removed.pop())
        self._trim_cuda()
        self.model_id = None

    def _trim_cuda(self):
        import torch
        gc.collect()
        if torch.cuda.is_initialized():
            if not self.models and self.model is None:
                # Torch 2.10 caches cuBLAS workspaces independently of empty_cache.
                # Captured graphs retain workspace pointers: clear only after ALL
                # models/graphs are disposed, never while another pin is alive.
                torch.cuda.synchronize()
                clear = getattr(torch._C, '_cuda_clearCublasWorkspaces', None)
                if clear is not None:
                    clear()
            torch.cuda.empty_cache()

    @staticmethod
    def _dispose(model):
        if callable(getattr(model, 'close', None)):
            model.close()
        elif hasattr(model, 'clear_voice_prompt_cache'):
            model.clear_voice_prompt_cache()

    def _load(self, model_id: str):
        if model_id not in MODELS:
            raise ValueError('Unknown model.')
        if self.model_id == model_id and self.model is not None:
            return
        if model_id in self.models:
            self.model_id, self.model = model_id, self.models[model_id]
            return
        from huggingface_hub import snapshot_download
        from faster_qwen3_tts import FasterQwen3TTS
        self._state('loading')
        if self.policy is None:
            self._unload()
        spec = MODELS[model_id]
        path = snapshot_download(model_id, revision=spec['revision'])
        model = FasterQwen3TTS.from_pretrained(path, backend='torch', max_seq_len=2048)
        try:
            model.warmup(prefill_len=100)
        except Exception:
            self._dispose(model)
            raise
        self.model = model
        self.models[model_id] = model
        self.model_id = model_id
        self.residency_errors.pop(model_id, None)
        self._state('ready')

    def load(self, model_id: str):
        with self.gate:
            try:
                self._load(model_id)
            except Exception as exc:
                self._discard(model_id)
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
        owned = getattr(self.session_owner, 'active', False)
        if not owned and not self._acquire(cancelled, emit):
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
            self.model.last_generation_stop_reason = None
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
            stop_reason = getattr(self.model, 'last_generation_stop_reason', None)
            if not cancelled.is_set() and stop_reason in {'max_new_tokens', 'max_seq_len'}:
                raise GenerationIncomplete(stop_reason, metrics(elapsed, duration, first_audio_ms))
            if not cancelled.is_set():
                emit({'type': 'done', 'model': request.model, 'sample_rate': rate,
                      'metrics': metrics(elapsed, duration, first_audio_ms)})
            self._state('ready')
        except GenerationIncomplete:
            self._state('ready')
            raise
        except Exception as exc:
            self._state('error', str(exc))
            raise
        finally:
            if not owned:
                try:
                    self._release_transient()
                finally:
                    self.gate.release()


def flatten_audio(audio):
    if isinstance(audio, list):
        return np.concatenate([np.asarray(part).reshape(-1) for part in audio]).astype(np.float32)
    return np.asarray(audio, dtype=np.float32).reshape(-1)
