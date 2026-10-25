"""Compile text/SSML/SSML-H to Qwen requests before taking the GPU lease."""
from __future__ import annotations

from contextlib import nullcontext
from dataclasses import asdict, dataclass, replace
from pathlib import Path
import queue
import re
import secrets
import tempfile
import threading
import time
from typing import Literal

import numpy as np
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from ssml_h import SSMLPlan, SSMLUnit, compile_ssml, ssml_capabilities

from . import audio
from .profiles import VoiceStore
from .runtime import GenerationIncomplete, GenerationRequest, LANGUAGES, MODELS, SPEAKERS, start_request_thread
from .text_planning import split_text

CUSTOM = 'Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice'
DIRECTED = 'Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice'
BASE = 'Qwen/Qwen3-TTS-12Hz-0.6B-Base'
DESIGN = 'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign'
DEFAULT_SAMPLE = 'Hello. This is my natural speaking voice, clear and steady, ready to tell you a story.'
NATIVE_LANGUAGES = dict(zip(SPEAKERS, ['Chinese'] * 5 + ['English', 'English', 'Japanese', 'Korean']))
LANGUAGE_CODES = dict(zip(['zh', 'en', 'ja', 'ko', 'de', 'fr', 'ru', 'pt', 'es', 'it'], LANGUAGES[1:]))
# Interoperability aliases select Qwen speakers, never OpenAI voice recordings.
VOICE_ALIASES = dict(zip(
    ['alloy', 'ash', 'ballad', 'coral', 'echo', 'fable', 'onyx', 'nova', 'sage', 'shimmer', 'verse', 'marin', 'cedar'],
    ['Ryan', 'Aiden', 'Ryan', 'Vivian', 'Aiden', 'Ryan', 'Uncle_Fu', 'Serena', 'Ryan', 'Vivian', 'Aiden', 'Vivian', 'Ryan']))
MODEL_ALIASES = {'qwen3-tts', 'faster-qwen3-tts', 'tts-1', 'tts-1-hd', 'gpt-4o-mini-tts'}


class SpeechRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', populate_by_name=True, allow_inf_nan=False)
    text: str = Field(min_length=1, max_length=50000)
    input_type: Literal['text', 'ssml', 'ssml-h'] = 'text'
    model: str = 'auto'
    mode: Literal['custom', 'clone', 'design'] | None = None
    voice: str = 'Ryan'
    voice_profile: str | None = None
    language: str = 'English'
    instruct: str = Field(default='', max_length=1500, validation_alias=AliasChoices('instruct', 'control', 'instructions'))
    ref_text: str = Field(default='', max_length=4000)
    ref_audio: str | None = Field(default=None, max_length=2048)
    xvec_only: bool = False
    non_streaming_mode: bool | None = None
    temperature: float = Field(default=.9, ge=.1, le=2)
    top_k: int = Field(default=50, ge=1, le=200)
    repetition_penalty: float = Field(default=1.05, ge=1, le=2)
    chunk_size: int = Field(default=8, ge=1, le=64)
    max_new_tokens: int = Field(default=360, ge=24, le=600)
    seed: int | None = Field(default=None, ge=0, le=2**32-1)
    randomize_seed: bool | None = None
    speed: float = Field(default=1, ge=.25, le=4)
    normalize_loudness: bool = False
    protect_long_audio: bool = True
    output_format: Literal['wav', 'mp3', 'flac', 'ogg', 'opus', 'aac', 'pcm'] = Field(
        default='wav', validation_alias=AliasChoices('output_format', 'format'))
    stream_format: Literal['mp3', 'pcm', 'opus', 'aac', 'flac', 'ogg'] = 'mp3'


@dataclass(frozen=True)
class Binding:
    name: str
    mode: str
    model: str
    speaker: str = 'Ryan'
    language: str = 'English'
    reference: bytes | None = None
    transcript: str = ''


@dataclass(frozen=True)
class PlannedSpeech:
    request: SpeechRequest
    plan: SSMLPlan
    bindings: dict[str, Binding]
    seed: int
    default: Binding


def language(value):
    if value in LANGUAGES:
        return value
    resolved = LANGUAGE_CODES.get(value.strip().lower().split('-')[0])
    if resolved is None:
        raise ValueError(f"Unsupported language '{value}'. Supported: {', '.join(LANGUAGES)}.")
    return resolved


def capabilities():
    result = ssml_capabilities(phoneme_alphabets=(), description_supported=True, turn_direction_supported=True)
    result['processor'] = {
        'name': 'qwen3-tts', 'phonemes': False, 'remote_audio': False,
        'voice_selection': 'Document definitions, unique saved names/ids, then Qwen native speakers.',
        'prosody': 'Rate and pitch use FFmpeg; volume is per-unit gain. No model-native speed scalar.',
        'direction': 'Base cloning and 1.7B CustomVoice accept delivery instructions. Base direction is experimental.',
        'native_voice_languages': NATIVE_LANGUAGES,
        'max_speech_units': 64, 'max_spoken_characters': 6000, 'max_output_seconds': 300,
        'implicit_handoff_ms': 120,
    }
    result['ssml_h']['default_voice_sample'] = {'language': 'English', 'text': DEFAULT_SAMPLE, 'used_when': 'h:sample is omitted'}
    result['ssml_h']['design_processor'] = {
        'model': DESIGN, 'clone_model': BASE,
        'descriptors': ['gender', 'age', 'pitch', 'style', 'languages', 'accent', 'dialect', 'description'],
        'values': 'Bounded natural-language descriptions, interpreted by VoiceDesign; results are probabilistic.',
    }
    return result


def design_description(definition):
    parts = [f'{key}: {getattr(definition, key)}' for key in ('gender', 'age', 'pitch', 'style', 'accent', 'dialect') if getattr(definition, key)]
    if definition.languages:
        parts.append('Languages: ' + ', '.join(definition.languages))
    if definition.description:
        parts.append(definition.description)
    result = '. '.join(parts)
    if not result:
        raise ValueError(f"Voice definition '{definition.name}' needs a description or design attributes.")
    if len(result) > 1500:
        raise ValueError('Combined voice description exceeds 1500 characters.')
    return result


class SpeechService:
    def __init__(self, engine, voices: VoiceStore):
        self.engine, self.voices = engine, voices

    def default_model(self, mode):
        return getattr(self.engine, 'workflow_models', {}).get(mode,
            {'custom': CUSTOM, 'clone': BASE, 'design': DESIGN}[mode])

    def prepare(self, request, reference=None):
        """No downloads, GPU calls, filesystem mutation or persistent writes."""
        default_language = language(request.language)
        profiles = self.voices.list()
        bindings = {}
        def resolve(name, definitions=frozenset()):
            if name in definitions:
                return None
            if name in bindings:
                return bindings[name]
            matches = [v for v in profiles if v['id'] == name or v['name'].casefold() == name.casefold()]
            native = next((s for s in SPEAKERS if s.casefold() == name.casefold()), VOICE_ALIASES.get(name.lower()))
            if len(matches) > 1 or (matches and native):
                raise ValueError(f"Voice '{name}' is ambiguous. Use its saved profile id.")
            if matches:
                v = matches[0]
                with self.voices.lock:
                    binding = Binding(name, 'clone', self.default_model('clone'), language=language(v.get('language') or default_language),
                                      reference=self.voices.audio(v), transcript=v.get('transcript', ''))
            elif native:
                binding = Binding(name, 'custom', self.default_model('custom'), speaker=native,
                                  language=NATIVE_LANGUAGES[native])
            else:
                raise ValueError(f"Unknown voice '{name}'. Choose a Qwen speaker or a saved profile.")
            bindings[name] = binding
            return binding

        if request.model not in MODELS and request.model not in MODEL_ALIASES and request.model != 'auto':
            raise ValueError(f"Unknown Qwen model '{request.model}'. See /v1/models.")
        mode = request.mode or (MODELS[request.model]['mode'] if request.model in MODELS else 'custom')
        if reference is not None:
            if not request.xvec_only and not request.ref_text.strip():
                raise ValueError('Transcript-guided cloning requires the exact reference transcript. Set xvec_only=true for identity-only cloning.')
            mode = 'clone'
            default = Binding('__reference__', mode, self.default_model('clone'), language=default_language, reference=reference, transcript=request.ref_text)
        elif request.voice_profile:
            default = resolve(request.voice_profile)
        elif mode == 'design':
            default = Binding('__design__', 'design', self.default_model('design'), language=default_language)
        else:
            default = resolve(request.voice)
            if mode == 'clone' and default.reference is None:
                raise ValueError('Cloning requires a saved voice or uploaded reference audio.')
        if request.model in MODELS:
            if MODELS[request.model]['mode'] != default.mode:
                raise ValueError('The selected model does not match the requested voice workflow.')
            default = replace(default, model=request.model)
        bindings[default.name] = default
        if request.input_type == 'text':
            plan = SSMLPlan('ssml', (SSMLUnit('speech', text=request.text, language=default_language, language_explicit=True),))
        else:
            plan = compile_ssml(request.text, request.input_type, default_language=default_language,
                                resolve_language=language, validate_voice=lambda n, d: resolve(n, d),
                                allow_turn_direction=request.input_type == 'ssml-h')
        definitions = {d.name: d for d in plan.voice_definitions}
        if len({n.casefold() for n in definitions}) != len(definitions):
            raise ValueError('Document voice names must be unique without regard to case.')
        for definition in plan.voice_definitions:
            if any(s.casefold() == definition.name.casefold() for s in SPEAKERS) or definition.name.lower() in VOICE_ALIASES:
                raise ValueError('Document definitions cannot shadow native voice names.')
            collisions = [v for v in profiles if v['name'].casefold() == definition.name.casefold() or v['id'] == definition.name]
            if collisions and not (definition.scope == 'profile' and definition.replace and len(collisions) == 1):
                raise ValueError(f"Voice '{definition.name}' already exists. Use scope=profile and replace=true to replace it.")
            design_description(definition)
            for lang in definition.languages:
                language(lang)
            if definition.sample_language:
                language(definition.sample_language)
        units = []
        for unit in plan.units:
            if unit.kind == 'break':
                units.append(unit)
                continue
            binding = default if not unit.voice else (None if unit.voice in definitions else resolve(unit.voice))
            effective_rate = unit.prosody.rate * request.speed
            if not .25 <= effective_rate <= 4:
                raise ValueError('Combined request speed and SSML rate must be between 0.25 and 4.')
            if request.protect_long_audio:
                target = max(4, min(50, request.max_new_tokens // 7))
                limit = max(target, min(80, request.max_new_tokens // 4))
                texts = list(split_text(unit.text, max_chars=400, target_units=target, limit_units=limit))
            else:
                texts = [re.sub(r'\s+', ' ', unit.text).strip()]
            if not request.protect_long_audio and len(texts[0]) > 1000:
                raise ValueError('Speech units exceed 1000 characters. Enable protect_long_audio or split the text.')
            for text in texts:
                compiled = replace(unit, text=text)
                if binding:
                    self.config(request, compiled, binding, 0)
                else:
                    self.config(request, compiled, Binding(unit.voice, 'clone', self.default_model('clone'), transcript='Bootstrap transcript'), 0)
                units.append(compiled)
        if not any(u.kind == 'speech' for u in units):
            raise ValueError('Add at least one speech turn.')
        if sum(u.kind == 'speech' for u in units) > 64 or sum(len(u.text) for u in units) > 6000:
            raise ValueError('A request supports at most 64 speech units and 6000 spoken characters.')
        seed = secrets.randbits(32) if request.seed is None or request.randomize_seed else request.seed
        return PlannedSpeech(request, replace(plan, units=tuple(units)), bindings, seed, default)

    def config(self, request, unit, binding, seed):
        lang = unit.language if unit.language_explicit else binding.language
        direction = unit.direction or request.instruct
        model = binding.model
        # A named native turn inherits the explicitly selected CustomVoice model.
        if binding.mode == 'custom' and request.model in MODELS and MODELS[request.model]['mode'] == 'custom':
            model = request.model
        elif binding.mode == 'custom' and direction and not MODELS[model]['instructions']:
            model = DIRECTED
        return GenerationRequest(
            mode=binding.mode, model=model, text=unit.text, language=lang or request.language,
            speaker=binding.speaker, instruct=direction, ref_text=binding.transcript,
            xvec_only=request.xvec_only or (binding.mode == 'clone' and not binding.transcript.strip()),
            non_streaming_mode=request.non_streaming_mode, temperature=request.temperature, top_k=request.top_k,
            repetition_penalty=request.repetition_penalty, chunk_size=request.chunk_size,
            max_new_tokens=request.max_new_tokens, seed=seed)

    def inspect(self, prepared):
        return {'input_type': prepared.request.input_type, 'seed': prepared.seed,
                'voices': list(prepared.plan.voices), 'languages': list(prepared.plan.languages),
                'voice_definitions': [asdict(d) for d in prepared.plan.voice_definitions],
                'units': [asdict(u) for u in prepared.plan.units]}

    def run(self, prepared, cancelled, emit, *, streaming=False, speech_index=None, retained=None, ids=None):
        started = time.perf_counter()
        request, plan = prepared.request, prepared.plan
        bindings = dict(prepared.bindings)
        pending, takes, output = [], {}, []
        timings, first_audio_ms, retries = [], None, 0
        lease = self.engine.session(cancelled, emit) if hasattr(self.engine, 'session') else nullcontext()
        with lease, tempfile.TemporaryDirectory(prefix='qwen-speech-') as temporary:
            queue_ms = (time.perf_counter() - started) * 1000
            references = {}
            duration = 0.

            def render(config, binding, *, stream=False, receive_audio=None, retry=True):
                nonlocal retries
                if cancelled.is_set():
                    raise InterruptedError('Generation cancelled.')
                path = None
                if binding.reference is not None:
                    if binding.name not in references:
                        path = Path(temporary) / f'reference-{len(references)}.wav'
                        path.write_bytes(binding.reference)
                        references[binding.name] = path
                    path = references[binding.name]
                parts = []
                def receive(event):
                    if event['type'] == 'chunk':
                        if event['sample_rate'] != audio.RATE:
                            raise RuntimeError('Unexpected Qwen sample rate.')
                        parts.append(np.asarray(event['audio'], dtype=np.float32))
                        if stream:
                            (receive_audio or publish)(parts[-1])
                    elif event['type'] == 'done':
                        timings.append(event.get('metrics', {}))
                    else:
                        emit(event)
                try:
                    self.engine.generate(config, path, cancelled, receive, stream)
                except GenerationIncomplete as exc:
                    timings.append(exc.metrics)
                    if stream or not retry or len(config.text.strip()) < 2 or cancelled.is_set():
                        raise
                    texts = list(split_text(config.text, max_chars=max(1, len(config.text) // 2),
                                            target_units=1, limit_units=80))
                    if not 2 <= len(texts) <= 3:
                        raise
                    retries += 1
                    emit({'type': 'retrying', 'message': 'Retrying a limited speech unit in smaller sections.'})
                    pieces = [render(config.model_copy(update={'text': text,
                                'seed': ((config.seed or 0) + index + 1) % 2**32}), binding, retry=False)
                              for index, text in enumerate(texts)]
                    return np.concatenate(list(audio.assemble(('speech', piece) for piece in pieces)))
                if cancelled.is_set():
                    raise InterruptedError('Generation cancelled.')
                if not parts:
                    raise RuntimeError('The model did not produce audio.')
                return np.concatenate(parts)

            def publish(array):
                nonlocal duration, first_audio_ms
                if first_audio_ms is None and len(array):
                    first_audio_ms = (time.perf_counter() - started) * 1000
                duration += len(array) / audio.RATE
                if duration > 300:
                    raise ValueError('Generated output exceeds the 300 second request limit.')
                output.append(array)
                emit({'type': 'chunk', 'audio': array, 'sample_rate': audio.RATE, 'duration_s': duration})

            for index, definition in enumerate(plan.voice_definitions):
                sample = definition.sample or DEFAULT_SAMPLE
                sample_language = language(definition.sample_language or
                    ((definition.languages[0] if definition.languages else request.language) if definition.sample else 'English'))
                design = replace(prepared.default, name=definition.name, mode='design', model=self.default_model('design'),
                                 reference=None, transcript='', language=sample_language)
                seed = definition.seed if definition.seed is not None else (prepared.seed + index) % 2**32
                bootstrap = request.model_copy(update={'model': self.default_model('design'), 'instruct': design_description(definition)})
                config = self.config(bootstrap, SSMLUnit('speech', text=sample), design, seed)
                emit({'type': 'designing', 'voice': definition.name})
                samples = render(config, design)
                if len(samples) / audio.RATE > 60:
                    raise ValueError('Designed voice bootstrap exceeds 60 seconds.')
                reference = audio.wav(samples)
                voice_language = language(definition.languages[0] if definition.languages else request.language)
                bindings[definition.name] = Binding(definition.name, 'clone', self.default_model('clone'), language=voice_language,
                                                    reference=reference, transcript=sample)
                if definition.scope == 'profile':
                    pending.append(({'name': definition.name, 'transcript': sample, 'language': voice_language,
                                     'profile_type': 'design', 'description': design_description(definition),
                                     'recipe': {'version': 1, 'workflow': 'design', 'selected_version': 'original',
                                                'settings': config.model_dump(), 'character': asdict(definition)}},
                                    reference, definition.replace))

            speech = [u for u in plan.units if u.kind == 'speech']
            if speech_index is not None:
                if speech_index >= len(speech):
                    raise ValueError('Magic speech_index does not identify a speech unit.')
                units = [speech[speech_index]]
            else:
                units = plan.units

            def timeline():
                index, timeline_frames = 0, 0
                for unit in units:
                    if cancelled.is_set():
                        raise InterruptedError('Generation cancelled.')
                    if unit.kind == 'break':
                        timeline_frames += round(audio.RATE * unit.duration_ms / 1000)
                        if timeline_frames > audio.RATE * 300:
                            raise ValueError('Generated output exceeds the 300 second request limit.')
                        yield 'break', unit.duration_ms
                        continue
                    take_id = ids[index] if ids else str(index)
                    seed_index = speech_index if speech_index is not None else index
                    seed = (prepared.seed + seed_index) % 2**32
                    binding = bindings.get(unit.voice) if unit.voice else prepared.default
                    if retained and take_id in retained:
                        seed, waveform = retained[take_id]
                    else:
                        emit({'type': 'turn', 'index': seed_index, 'voice': binding.name, 'seed': seed})
                        waveform = render(self.config(request, unit, binding, seed), binding)
                        waveform = audio.effects(waveform, rate=unit.prosody.rate * request.speed,
                                                 pitch=unit.prosody.pitch_semitones, volume=unit.prosody.volume)
                    takes[take_id] = (seed, waveform)
                    timeline_frames += len(waveform)
                    if timeline_frames > audio.RATE * 300:
                        raise ValueError('Generated output exceeds the 300 second request limit.')
                    index += 1
                    yield 'speech', waveform
            def incremental(emit_audio):
                previous, gap = False, None
                last_speech = max(index for index, unit in enumerate(units) if unit.kind == 'speech')
                speech_number = 0
                for index, unit in enumerate(units):
                    if cancelled.is_set():
                        raise InterruptedError('Generation cancelled.')
                    if unit.kind == 'break':
                        gap = (gap or 0) + unit.duration_ms
                        continue
                    pause = gap if gap is not None else 120 if previous else 0
                    if pause:
                        emit_audio(np.zeros(round(audio.RATE * pause / 1000), dtype=np.float32))
                    boundary = audio.UnitBoundary(emit_audio, leading=previous, trailing=index != last_speech)
                    seed_index = speech_index if speech_index is not None else speech_number
                    seed = (prepared.seed + seed_index) % 2**32
                    binding = bindings.get(unit.voice) if unit.voice else prepared.default
                    emit({'type': 'turn', 'index': seed_index, 'voice': binding.name, 'seed': seed})
                    config = self.config(request, unit, binding, seed)
                    neutral = unit.prosody.is_neutral and request.speed == 1
                    if neutral:
                        waveform = render(config, binding, stream=True, receive_audio=boundary.feed)
                    else:
                        processed = []
                        def receive_processed(samples):
                            processed.append(samples)
                            boundary.feed(samples)
                        filters = audio.effect_filters(rate=unit.prosody.rate * request.speed,
                            pitch=unit.prosody.pitch_semitones, volume=unit.prosody.volume)
                        with audio.StreamingFilter(receive_processed, cancelled, ','.join(filters)) as shaper:
                            render(config, binding, stream=True, receive_audio=shaper.feed)
                        waveform = np.concatenate(processed) if processed else np.empty(0, dtype=np.float32)
                    boundary.finish()
                    takes[str(speech_number)] = (seed, waveform)
                    speech_number += 1
                    previous, gap = True, None
                if gap:
                    emit_audio(np.zeros(round(audio.RATE * gap / 1000), dtype=np.float32))

            if streaming and ids is None:
                if request.normalize_loudness:
                    with audio.StreamingFilter(publish, cancelled, 'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=24000') as normalizer:
                        incremental(normalizer.feed)
                else:
                    incremental(publish)
            elif request.normalize_loudness:
                waveform = np.concatenate(list(audio.assemble(timeline())))
                publish(audio.effects(waveform, normalize=True))
            else:
                for array in audio.assemble(timeline()):
                    publish(array)
            if cancelled.is_set():
                raise InterruptedError('Generation cancelled.')
            total_ms = (time.perf_counter() - started) * 1000
            load_ms = sum(t.get('model_load_ms', 0) for t in timings)
            generation_ms = max(0, total_ms - queue_ms - load_ms)
            metrics = {'duration_s': round(duration, 3), 'generation_ms': round(generation_ms),
                       'total_ms': round(total_ms), 'queue_ms': round(queue_ms), 'model_load_ms': round(load_ms),
                       'ttfa_ms': round(first_audio_ms or 0),
                       'speed': round(duration / (generation_ms / 1000), 3) if generation_ms else 0,
                       'reference_preparation_ms': sum(t.get('reference_preparation_ms') or 0 for t in timings),
                       'reference_cache_hit': next((t.get('reference_cache_hit') for t in reversed(timings) if t.get('reference_cache_hit') is not None), None),
                       'seed': prepared.seed, 'speech_units': len(speech), 'voices': list(plan.voices),
                       'retries': retries,
                       'languages': list(plan.languages)}
            emit({'type': 'done', 'metrics': metrics})
            return {'audio': np.concatenate(output), 'takes': takes, 'pending': pending, 'metrics': metrics,
                    'seed': prepared.seed}


def start_worker(service, prepared, **options):
    events, cancelled = queue.Queue(maxsize=16), threading.Event()
    def emit(event):
        while not cancelled.is_set():
            try:
                events.put(event, timeout=.2)
                return
            except queue.Full:
                pass
    def work():
        try:
            result = service.run(prepared, cancelled, emit, **options)
            emit({'type': 'result', 'result': result})
        except Exception as exc:
            emit({'type': 'error', 'message': str(exc), 'status_code': getattr(exc, 'status_code', 503)})
        finally:
            emit({'type': 'finished'})
    start_request_thread(service.engine, work, name='qwen-speech-request')
    return events, cancelled
