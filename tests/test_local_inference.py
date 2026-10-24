"""Exercise the installed local model package without network or model assets."""
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from transformers import MimiConfig, MimiModel

import faster_qwen3_tts
import qwen_tts
from qwen_tts import Qwen3TTSTokenizer
from qwen_tts._transformers_compat import restore_mimi_full_attention, restore_rope_buffers
from qwen_tts.core.models.configuration_qwen3_tts import Qwen3TTSTalkerConfig
from qwen_tts.core.models.modeling_qwen3_tts import Qwen3TTSRotaryEmbedding


def test_both_packages_belong_to_our_installed_distribution():
    # A mounted development tree can carry generated egg-info. Inspect the
    # installed wheel even when PYTHONPATH intentionally loads source modules.
    wheels = [dist for dist in metadata.distributions()
              if dist.metadata['Name'].lower().replace('_', '-') == 'faster-qwen3-tts'
              and dist.read_text('WHEEL') is not None]
    assert len(wheels) == 1
    distribution = wheels[0]
    installed = {str(path).replace('\\', '/') for path in distribution.files}
    assert 'qwen_tts/core/models/modeling_qwen3_tts.py' in installed
    assert 'qwen_tts/_transformers_compat.py' in installed
    assert 'faster_qwen3_tts/upstreams.toml' in installed
    assert Path(qwen_tts.__file__).parent.parent == Path(faster_qwen3_tts.__file__).parent.parent
    names = {dist.metadata['Name'].lower().replace('_', '-') for dist in metadata.distributions()}
    assert not names.intersection({'qwen-tts', 'qwen-tts-hf', 'gradio', 'gradio-client',
                                   'qwentts-cpp-python', 'onnxruntime', 'sox', 'torchaudio'})


def test_real_mimi_checkpoint_restores_full_attention(tmp_path):
    config = MimiConfig(hidden_size=16, num_filters=8, upsampling_ratios=[2, 2],
                        codebook_size=16, codebook_dim=16, vector_quantization_hidden_dimension=16,
                        num_quantizers=2, num_semantic_quantizers=1, upsample_groups=16,
                        num_hidden_layers=1, intermediate_size=32, num_attention_heads=2,
                        num_key_value_heads=2, head_dim=8, max_position_embeddings=64,
                        sliding_window=8, rope_theta=10000.0)
    original = MimiModel(config)
    original.save_pretrained(tmp_path)
    loaded = MimiModel.from_pretrained(tmp_path, local_files_only=True)
    restore_mimi_full_attention(loaded)
    assert loaded.config.sliding_window == 64
    windows = [module.sliding_window for module in loaded.modules() if hasattr(module, 'sliding_window')]
    assert windows and all(window == 64 for window in windows)


def test_real_qwen_rotary_buffers_restore_position_dependent_output():
    config = Qwen3TTSTalkerConfig(hidden_size=16, num_attention_heads=2, max_position_embeddings=64)
    rotary = Qwen3TTSRotaryEmbedding(config)
    expected = rotary.inv_freq.clone()
    rotary.inv_freq.zero_()
    restore_rope_buffers(rotary)
    torch.testing.assert_close(rotary.inv_freq, expected)
    assert rotary.original_inv_freq is rotary.inv_freq
    cosine, sine = rotary(torch.zeros(1, 3, 16), torch.tensor([[0, 1, 2]]))
    assert (cosine[:, 0] == 1).all() and (sine[:, 0] == 0).all()
    assert torch.count_nonzero(sine[:, 1])


@pytest.mark.parametrize('representation', ['output', 'dict', 'list', 'tensor'])
def test_12hz_decode_preserves_single_and_batch_codec_layout(representation):
    first = torch.arange(12).reshape(3, 4)
    second = torch.arange(8).reshape(2, 4)
    captured = []

    class Codec:
        def get_model_type(self):
            return 'qwen3_tts_tokenizer_12hz'

        def decode(self, codes, return_dict):
            captured.append(codes)
            assert return_dict
            return SimpleNamespace(audio_values=[torch.zeros(24) for _ in codes])

        def get_output_sample_rate(self):
            return 24000

    tokenizer = Qwen3TTSTokenizer()
    tokenizer.model = Codec()
    tokenizer.device = torch.device('cpu')
    payload = {'output': SimpleNamespace(audio_codes=[first, second]),
               'dict': {'audio_codes': [first.numpy(), second.numpy()]},
               'list': [{'audio_codes': first}, {'audio_codes': second}],
               'tensor': {'audio_codes': first}}[representation]
    audio, rate = tokenizer.decode(payload)
    expected_batch = 1 if representation == 'tensor' else 2
    assert captured[0].shape == (expected_batch, 3, 4)
    assert torch.equal(captured[0][0], first)
    if expected_batch == 2:
        assert torch.equal(captured[0][1, :2], second)
        assert (captured[0][1, 2] == -1).all()
    assert rate == 24000 and len(audio) == expected_batch
    assert all(waveform.dtype == np.float32 for waveform in audio)


def test_12hz_decode_rejects_legacy_flat_codes():
    tokenizer = Qwen3TTSTokenizer()
    tokenizer.model = SimpleNamespace(get_model_type=lambda: 'qwen3_tts_tokenizer_12hz')
    tokenizer.device = torch.device('cpu')
    with pytest.raises(ValueError, match='12 Hz audio codes'):
        tokenizer.decode({'audio_codes': torch.arange(8)})
