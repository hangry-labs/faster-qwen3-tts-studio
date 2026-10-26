"""Decoder windows change waveform reconstruction, never token sampling controls."""
from types import SimpleNamespace
import inspect
import threading

import numpy as np
import pytest
import torch
from pydantic import ValidationError

from faster_qwen3_tts.model import FasterQwen3TTS
from faster_qwen3_tts.standalone_ui.api import OpenAISpeechRequest
from faster_qwen3_tts.standalone_ui.runtime import GenerationRequest, StudioEngine
from faster_qwen3_tts.standalone_ui.speech import SpeechRequest


METHODS = ['custom_voice', 'voice_design', 'voice_clone']


@pytest.mark.parametrize('method', METHODS)
@pytest.mark.parametrize('context', [25, 100, 200])
def test_real_streaming_wrapper_uses_bounded_window_and_preserves_sample_count(monkeypatch, method, context):
    from faster_qwen3_tts import streaming
    windows, sampling = [], []
    class Tokenizer:
        def decode(self, payload):
            frames = payload['audio_codes'].shape[1]
            windows.append(frames)
            return [torch.zeros(frames * 2)], 24000
    prepared = SimpleNamespace(speech_tokenizer=Tokenizer())
    model = object.__new__(FasterQwen3TTS)
    model.model = SimpleNamespace(model=SimpleNamespace(tts_model_type={
        'custom_voice': 'custom_voice', 'voice_design': 'voice_design', 'voice_clone': 'base'}[method],
        tts_model_size='1b7'), _validate_languages=lambda _: None, _validate_speakers=lambda _: None)
    model.predictor_graph = model.talker_graph = object()
    model._prepare_generation_custom = lambda **kwargs: (prepared,) + (None,) * 6
    model._prepare_generation = lambda **kwargs: (prepared,) + (None,) * 7
    def codes(**kwargs):
        sampling.append(kwargs)
        for _ in range(20):
            yield torch.zeros(12, 16, dtype=torch.long), {}
    monkeypatch.setattr(streaming, 'fast_generate_streaming', codes)
    kwargs = dict(text='Example.', language='English', chunk_size=12)
    if method == 'custom_voice':
        kwargs['speaker'] = 'Ryan'
    if method == 'voice_design':
        kwargs['instruct'] = 'A warm narrator.'
    generate = getattr(model, f'generate_{method}_streaming')
    chunks = list(generate(**kwargs, decoder_context_frames=context))
    assert sum(len(wave) for wave, _, _ in chunks) == 480
    assert len(chunks) == 20
    assert windows[-1] == context + 12
    assert max(windows) <= context + 12
    assert 'decoder_context_frames' not in sampling[0]
    if context == 25:
        windows.clear()
        assert len(list(generate(**kwargs))) == 20
        assert windows[-1] == 37
    assert inspect.signature(generate).parameters['decoder_context_frames'].default == 25


@pytest.mark.parametrize('value', [True, False, 0, -1, 201, 25.0, '100', None])
@pytest.mark.parametrize('method', METHODS)
def test_core_rejects_invalid_context_before_preparing_model(method, value):
    model = object.__new__(FasterQwen3TTS)
    kwargs = {'text': 'Test', 'speaker': 'Ryan'} if method == 'custom_voice' else {'text': 'Test', 'instruct': 'Warm'} if method == 'voice_design' else {'text': 'Test'}
    kwargs['language'] = 'English'
    with pytest.raises(ValueError, match='integer from 1 to 200'):
        next(getattr(model, f'generate_{method}_streaming')(**kwargs, decoder_context_frames=value))


@pytest.mark.parametrize('schema, required', [
    (GenerationRequest, {'text': 'Test'}), (SpeechRequest, {'text': 'Test'}),
    (OpenAISpeechRequest, {'model': 'tts-1', 'input': 'Test', 'voice': 'Ryan'}),
])
def test_api_schemas_share_strict_bounded_default(schema, required):
    assert schema(**required).decoder_context_frames == 25
    assert schema(**required, decoder_context_frames=100).decoder_context_frames == 100
    for invalid in [True, 0, 201, 25.5, '100']:
        with pytest.raises(ValidationError):
            schema(**required, decoder_context_frames=invalid)


@pytest.mark.parametrize('streaming', [True, False])
def test_engine_passes_context_only_to_streaming_method(monkeypatch, streaming):
    received = []
    class Model:
        def generate_custom_voice_streaming(self, **kwargs):
            received.append(kwargs)
            yield np.zeros(100, dtype=np.float32), 24000, {}
        def generate_custom_voice(self, **kwargs):
            received.append(kwargs)
            return np.zeros(100, dtype=np.float32), 24000
    engine = StudioEngine()
    engine.model = Model()
    monkeypatch.setattr(engine, '_load', lambda _: None)
    monkeypatch.setattr(torch.cuda, 'manual_seed_all', lambda _: None)
    engine.generate(GenerationRequest(text='Test', decoder_context_frames=100), None,
                    threading.Event(), lambda event: None, streaming)
    assert received[0].get('decoder_context_frames') == (100 if streaming else None)
