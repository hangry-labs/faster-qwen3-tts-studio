import torch
from transformers.modeling_rope_utils import ROPE_INIT_FUNCTIONS

from qwen_tts._transformers_compat import (
    patch_transformers_rope_registry,
    restore_mimi_full_attention,
    restore_rope_buffers,
)


class _RopeModule(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.config = object()
        self.register_buffer("inv_freq", torch.zeros(2), persistent=False)
        self.original_inv_freq = self.inv_freq
        self.attention_scaling = 0.0

    @staticmethod
    def rope_init_fn(config, device):
        del config
        return torch.tensor([1.0, 0.5], device=device), 1.0


class _MimiModule(torch.nn.Module):
    __module__ = "transformers.models.mimi.modeling_mimi"

    def __init__(self):
        super().__init__()
        self.config = type("Config", (), {"max_position_embeddings": 8000, "sliding_window": 250})()
        self.sliding_window = 250


def test_restore_rope_buffers():
    model = torch.nn.Sequential(_RopeModule())

    restore_rope_buffers(model)

    torch.testing.assert_close(model[0].inv_freq, torch.tensor([1.0, 0.5]))
    assert model[0].original_inv_freq is model[0].inv_freq
    assert model[0].attention_scaling == 1.0


def test_default_rope_initializer_is_registered():
    patch_transformers_rope_registry()

    assert "default" in ROPE_INIT_FUNCTIONS


def test_restore_mimi_full_attention():
    model = torch.nn.Sequential(_MimiModule())

    restore_mimi_full_attention(model)

    assert model[0].config.sliding_window == 8000
    assert model[0].sliding_window == 8000
