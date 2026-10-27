"""Incremental token stability, bounded waits and reference conditioning parity."""
from types import SimpleNamespace
import threading
import time

import pytest
import torch
from tokenizers import Tokenizer, models, pre_tokenizers, trainers
from transformers import PreTrainedTokenizerFast

from faster_qwen3_tts.live_input import LiveConditioning, TextInput
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSForConditionalGeneration


@pytest.fixture(scope='module')
def tokenizer():
    value = Tokenizer(models.BPE(unk_token='[UNK]'))
    value.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    trainer = trainers.BpeTrainer(vocab_size=400, special_tokens=['[UNK]'],
                                  initial_alphabet=pre_tokenizers.ByteLevel.alphabet())
    value.train_from_iterator(['Good morning. I left the window open. Hello world!',
                              "I can't believe we're ready. Café déjà vu.",
                              '你好，今天的天气不错。日本語の文章です。Привет, мир!'], trainer)
    return PreTrainedTokenizerFast(tokenizer_object=value, unk_token='[UNK]')


@pytest.mark.parametrize('text', ['Hello world! Good morning.', "I can't believe we're ready.",
                                  '你好，今天的天气不错。', 'Café déjà vu. Привет, мир!', 'A  B\n\nC\tD   '])
@pytest.mark.parametrize('size', [1, 2, 7])
def test_fragment_sizes_preserve_canonical_tokens(tokenizer, text, size):
    source = TextInput()
    source.attach(tokenizer)
    for offset in range(0, len(text), size):
        source.append(text[offset:offset+size])
    source.finish()
    assert source.tokens == tokenizer.encode(text, add_special_tokens=False)


def test_input_can_arrive_before_model_is_ready(tokenizer):
    source = TextInput()
    source.append('Hello world!')
    source.finish()
    source.attach(tokenizer)
    ids, finished = source.initial(100)
    assert finished and ids == tokenizer.encode('Hello world!', add_special_tokens=False)


def test_limits_and_empty_finish_are_explicit(tokenizer):
    source = TextInput(max_chars=3)
    with pytest.raises(ValueError, match='character limit'):
        source.append('four')
    with pytest.raises(ValueError, match='some text'):
        source.finish()
    source = TextInput(max_tokens=1)
    source.attach(tokenizer)
    with pytest.raises(ValueError, match='token limit'):
        source.append('1 2 3 4 5 6 7 8 9 ')


def test_idle_timeout_is_reset_by_real_input_only(tokenizer):
    source = TextInput(idle_timeout=.04)
    source.attach(tokenizer)
    source.append('Hello ')
    source.last_input -= .05
    source.active_since -= .05
    with pytest.raises(TimeoutError, match='input timeout'):
        source.append('')


def test_cancel_wakes_waiter_and_finished_input_does_not_idle_timeout(tokenizer):
    source = TextInput()
    source.attach(tokenizer)
    timer = threading.Timer(.02, source.cancel)
    timer.start()
    with pytest.raises(InterruptedError):
        source.initial(2)
    timer.join()
    source = TextInput(idle_timeout=.01)
    source.append('Hello.')
    source.finish()
    source.attach(tokenizer)
    source.last_input -= 10
    assert source.initial(100)[1]
    source.active_since -= source.max_seconds+1
    with pytest.raises(TimeoutError, match='wall time'):
        source.check()


def model_stub():
    torch.manual_seed(23)
    text = torch.nn.Embedding(100, 4)
    codec = torch.nn.Embedding(100, 4)
    residual = torch.nn.Embedding(100, 4)
    talker = SimpleNamespace(device='cpu', get_text_embeddings=lambda: text, text_projection=torch.nn.Identity(),
        get_input_embeddings=lambda: codec, config=SimpleNamespace(num_code_groups=2),
        code_predictor=SimpleNamespace(get_input_embeddings=lambda: [residual]))
    return SimpleNamespace(talker=talker, config=SimpleNamespace(talker_config=SimpleNamespace(codec_bos_id=2)))


@pytest.mark.parametrize('xvec_only', [False, True])
def test_live_runtime_rejects_06_before_loading_or_queueing(monkeypatch, xvec_only):
    from faster_qwen3_tts.standalone_ui.runtime import GenerationRequest, StudioEngine
    engine = StudioEngine()
    monkeypatch.setattr(engine, 'admit', lambda: pytest.fail('Unsupported model entered the queue'))
    monkeypatch.setattr(engine, '_load', lambda model: pytest.fail('Unsupported model loaded'))
    request = GenerationRequest(mode='clone', model='Qwen/Qwen3-TTS-12Hz-0.6B-Base',
                                text='Hello.', ref_text='Reference.', xvec_only=xvec_only, seed=4210)
    with pytest.raises(ValueError, match='supports only.*1.7B-Base'):
        engine.generate_live(request, None, TextInput(), lambda event: None)


@pytest.mark.parametrize('ref_length,codec_length,target_length,finished',
                         [(4,10,15,False), (4,10,3,True), (12,3,8,False), (12,3,8,True)])
def test_live_icl_matches_original_reference_layout(ref_length, codec_length, target_length, finished):
    model = model_stub()
    target = list(range(20,20+target_length))
    reference = torch.tensor([list(range(3,3+ref_length))])
    codes = torch.arange(codec_length*2).reshape(codec_length,2)
    pad, eos = torch.zeros(1,1,4), torch.ones(1,1,4)
    expected_prefix, expected_tail = Qwen3TTSForConditionalGeneration.generate_icl_prompt(model,
        text_id=torch.tensor([target]), ref_id=reference, ref_code=codes,
        tts_pad_embed=pad, tts_eos_embed=eos, non_streaming_mode=False)
    count = len(target) if finished else max(1,codec_length+1-ref_length)
    source = SimpleNamespace(check=lambda: None, next_token=lambda offset: target[offset] if offset < len(target) else None)
    live = LiveConditioning(model, source, target[:count], finished)
    prefix, _ = live.build_icl(ref_id=reference, ref_code=codes, tts_pad_embed=pad, tts_eos_embed=eos)
    assert torch.equal(prefix, expected_prefix)
    for i in range(expected_tail.shape[1]):
        assert torch.equal(live.next_embedding(i), expected_tail[:,i:i+1])
    assert live.eos_consumed
    assert torch.equal(live.next_embedding(999),pad)


@pytest.mark.parametrize('error', [TimeoutError, InterruptedError, ValueError, RuntimeError])
def test_live_failure_releases_inference_frames_before_model_disposal(monkeypatch, error):
    import weakref
    from faster_qwen3_tts import live_input
    from faster_qwen3_tts.standalone_ui.runtime import GenerationRequest, StudioEngine

    engine = StudioEngine()
    request = GenerationRequest(mode='clone', model='Qwen/Qwen3-TTS-12Hz-1.7B-Base',
                                text='Hello.', ref_text='Reference.', seed=4210)
    engine.model = SimpleNamespace(last_generation_stop_reason=None)
    engine.model_id = request.model
    monkeypatch.setattr(engine, '_load', lambda model: None)
    monkeypatch.setattr(torch.cuda, 'manual_seed_all', lambda seed: None)
    references, released = [], []

    class InferenceResource:
        pass

    def fail(*args):
        resource = InferenceResource()
        references.append(weakref.ref(resource))
        raise error('Stopped while waiting for text.')
        yield  # This resource belongs to an inference generator frame.

    monkeypatch.setattr(live_input, 'generate_voice_clone_live', fail)
    monkeypatch.setattr(engine, '_release_transient', lambda: released.append(references[0]() is None))
    with pytest.raises(error, match='waiting for text'):
        engine.generate_live(request, None, TextInput(), lambda event: None)
    assert released == [True]
    assert not engine.gate.locked()
