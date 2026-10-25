"""Actual decode-loop stop causes and bounded incomplete-output handling."""
from contextlib import contextmanager
from types import SimpleNamespace
import threading

import numpy as np
import pytest
import torch

from faster_qwen3_tts import generate, streaming
from faster_qwen3_tts.standalone_ui.profiles import VoiceStore
from faster_qwen3_tts.standalone_ui.runtime import GenerationIncomplete, GenerationRequest, StudioEngine
from faster_qwen3_tts.standalone_ui.speech import SpeechRequest, SpeechService


@pytest.mark.parametrize('stream', [False, True])
@pytest.mark.parametrize('reason', ['eos', 'max_new_tokens', 'max_seq_len'])
def test_real_decode_loop_distinguishes_termination_causes(monkeypatch, stream, reason):
    module = streaming if stream else generate
    tokens = iter([1, 1, 7] if reason == 'eos' else [1] * 10)
    monkeypatch.setattr(module, 'sample_logits', lambda *args, **kwargs: torch.tensor([next(tokens)]))
    monkeypatch.setattr(torch.cuda, 'synchronize', lambda: None)
    embed = lambda tokens: torch.zeros(*tokens.shape, 4)
    predictor = SimpleNamespace(get_input_embeddings=lambda: [embed])
    talker = SimpleNamespace(code_predictor=predictor,
        get_input_embeddings=lambda: embed, codec_head=lambda hidden: torch.zeros(1, 1030),
        forward=lambda **kwargs: SimpleNamespace(logits=torch.zeros(1, 1, 1030), past_key_values=None,
                                                past_hidden=torch.zeros(1, 1, 4), generation_step=0))
    graph = SimpleNamespace(prefill_kv=lambda kv: 1, set_generation_state=lambda *args: None,
        max_seq_len=3 if reason == 'max_seq_len' else 100,
        run=lambda *args, **kwargs: torch.zeros(1, 1, 4))
    kwargs = dict(talker=talker, talker_input_embeds=torch.zeros(1, 1, 4), attention_mask=torch.ones(1, 1),
        trailing_text_hiddens=torch.zeros(1, 1, 4), tts_pad_embed=torch.zeros(1, 1, 4),
        config=SimpleNamespace(codec_eos_token_id=7, num_code_groups=2, vocab_size=1030),
        predictor_graph=SimpleNamespace(run=lambda value: torch.tensor([2])), talker_graph=graph,
        max_new_tokens=2 if reason != 'max_seq_len' else 5, repetition_penalty=1)
    if stream:
        chunks = list(streaming.fast_generate_streaming(**kwargs, chunk_size=2))
        assert chunks[-1][1]['is_final']
        assert chunks[-1][1]['stop_reason'] == reason
        assert sum(len(chunk) for chunk, timing in chunks) == 2
    else:
        codes, timing = generate.fast_generate(**kwargs)
        assert timing['stop_reason'] == reason and len(codes) == 2


def test_incomplete_complete_generation_retries_smaller_units_before_publishing(tmp_path):
    attempts, events = [], []
    class Engine:
        @contextmanager
        def session(self, cancelled, emit):
            yield

        def generate(self, config, reference, cancelled, emit, streaming):
            attempts.append(config.text)
            emit({'type': 'chunk', 'audio': np.ones(2400, dtype=np.float32) * .1, 'sample_rate': 24000})
            if len(attempts) == 1:
                raise GenerationIncomplete('max_new_tokens', {})
            emit({'type': 'done', 'metrics': {}})
    service = SpeechService(Engine(), VoiceStore(tmp_path))
    result = service.run(service.prepare(SpeechRequest(text='First sentence. Second sentence.', seed=42)),
                         threading.Event(), events.append)
    assert len(attempts) == 3
    assert attempts[1:] == ['First sentence.', 'Second sentence.']
    assert result['metrics']['retries'] == 1
    assert len(result['audio']) == 2400 * 2 + 2880
    assert sum(event['type'] == 'chunk' for event in events) == 1


def test_failed_retry_stops_instead_of_recursing_forever(tmp_path):
    class Engine:
        calls = 0
        def generate(self, *args):
            self.calls += 1
            raise GenerationIncomplete('max_new_tokens', {})
    engine = Engine()
    service = SpeechService(engine, VoiceStore(tmp_path))
    with pytest.raises(GenerationIncomplete):
        service.run(service.prepare(SpeechRequest(text='First sentence. Second sentence.')),
                    threading.Event(), lambda event: None)
    assert engine.calls == 2


def test_model_limit_releases_lease_and_does_not_mark_model_broken(monkeypatch):
    class Model:
        def generate_custom_voice(self, **kwargs):
            self.last_generation_stop_reason = 'max_new_tokens'
            return [np.ones(2400, dtype=np.float32)], 24000
    engine = StudioEngine()
    engine.model = Model()
    monkeypatch.setattr(engine, '_load', lambda model: None)
    with pytest.raises(GenerationIncomplete):
        engine.generate(GenerationRequest(text='Hello'), None, threading.Event(), lambda event: None, False)
    assert not engine.gate.locked() and not engine.waiters
    assert engine.status()['state'] == 'ready'
