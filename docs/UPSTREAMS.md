# Upstream source provenance

Hangry Labs maintains the model implementation and accelerated inference source
in this repository. Builds install both local packages from this checkout. They
do not install `qwen-tts`, `qwen-tts-hf`, or `faster-qwen3-tts` from another
publisher, clone another inference repository, or apply remote patches at startup.
Model checkpoints remain separate, pinned Hugging Face assets.

## Three maintained upstreams

| Upstream | Last incorporated revision | Local responsibility |
| --- | --- | --- |
| [QwenLM/Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) | [`022e286`](https://github.com/QwenLM/Qwen3-TTS/tree/022e286b98fbec7e1e916cb940cdf532cd9f488e) | Model/configuration/processor, inference wrapper, speaker encoder and 12 Hz speech codec in `src/qwen_tts/` |
| [andimarafioti/Qwen3-TTS](https://github.com/andimarafioti/Qwen3-TTS/tree/distribution/qwen-tts-hf), branch `distribution/qwen-tts-hf` | [`af457d9`](https://github.com/andimarafioti/Qwen3-TTS/tree/af457d954d8ce797603c6f260c3f911a09b1d90a) | Transformers 5 compatibility in the same local model package |
| [andimarafioti/faster-qwen3-tts](https://github.com/andimarafioti/faster-qwen3-tts) | [`1094aab`](https://github.com/andimarafioti/faster-qwen3-tts/tree/1094aabd83b367b1b29942769141b0524bed245d), version 0.5.4 | Static caches, CUDA graphs, generation and streaming in `src/faster_qwen3_tts/` |

Exact machine-readable revisions ship in
[`upstreams.toml`](../src/faster_qwen3_tts/upstreams.toml). They record the last
incorporated source, not a claim that we continually track a moving branch.

The compatibility branch contains the official base plus three commits:

1. [`00969da`](https://github.com/andimarafioti/Qwen3-TTS/commit/00969daa8064e23adc9e5f52cdf20cf247f94159): the runtime patch proposed in [Qwen PR #360](https://github.com/QwenLM/Qwen3-TTS/pull/360).
2. [`a466278`](https://github.com/andimarafioti/Qwen3-TTS/commit/a466278d04ce9693395947906a949f744acd41e8): packaging and publication of `qwen-tts-hf`.
3. [`af457d9`](https://github.com/andimarafioti/Qwen3-TTS/commit/af457d954d8ce797603c6f260c3f911a09b1d90a): release artifact download correction.

The runtime patch is already included in our imported source. It is not applied
twice. Its RoPE initialization/buffer restoration and Mimi full-attention fixes
preserve behavior expected by the checkpoints under Transformers 5. The other
two commits provide distribution provenance; their publishing workflow is not
part of our product.

## Local boundaries

- `src/qwen_tts/`: locally maintained Qwen inference source. Original file names
  and imports are retained to make upstream differences easier to review.
- `src/faster_qwen3_tts/`: acceleration and the Hangry Labs Studio. The Studio
  remains under `standalone_ui/`; both packages ship in one Python distribution.
- `tests/`: Studio, cache, local inference, compatibility and GPU parity checks.
- `scripts/`: Docker lifecycle, notices, model prefetch and speech smoke tooling.
- `benchmarks/`: manual product measurements adapted from VoxCPMTTS;
  `benchmarks/research/` retains the inherited NVIDIA investigations separately.

Local changes omit the upstream Gradio demo/launcher, training tools and package
publisher. The unused 25 Hz codec and its assets/imports are omitted; this Studio
supports the five catalogued 12 Hz checkpoints. The 12 Hz tokenizer wrapper is
adapted accordingly and the local package version identifies Hangry Labs changes.
GGML/GGUF/native platform adapters, host setup scripts and local-ASR helpers are
also removed. General libraries such as Torch, Transformers and Librosa remain
ordinary dependencies. Gradio, ONNX Runtime, Python SoX and TorchAudio are not
required by this runtime.

The streaming fork and other inspiration credited in [NOTICE](../NOTICE) remain
part of our source attribution. They are distinct from these three ongoing
upstream synchronization sources.
