# Engine and Python reference

The supported product is the [NVIDIA Docker Studio](../README.md). Both the model
implementation and faster generation path are maintained locally. See
[upstream source provenance](UPSTREAMS.md) for incorporated revisions.

## Source layout

`src/qwen_tts/` contains the Qwen model, configuration, processor, inference
wrapper, speaker encoder, 12 Hz tokenizer and Transformers 5 compatibility fixes.
`src/faster_qwen3_tts/` contains static-cache generation, CUDA graph capture,
chunked decoding and Studio. Both are installed by the same distribution.
Do not install a separate `qwen-tts` or `qwen-tts-hf` wheel into this environment.

Python 3.13 and NVIDIA CUDA are the supported runtime. Docker applies the core
pins in `requirements.runtime.txt`. PyTorch and Transformers remain dependencies;
model weights are the original pinned Qwen checkpoints.

## Generation

Inside the installed Docker runtime:

```python
import soundfile as sf
from faster_qwen3_tts import FasterQwen3TTS

model = FasterQwen3TTS.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-0.6B-Base", device="cuda:0"
)
audio, sample_rate = model.generate_voice_clone(
    text="Welcome to the workshop.",
    language="English",
    ref_audio="authorized-reference.wav",
    ref_text="The exact words in that recording.",
    instruct="Speak warmly and clearly.",
    xvec_only=False,
    non_streaming_mode=False,
)
sf.write("speech.wav", audio[0], sample_rate)
```

The CLI also runs inside Docker:

```bash
faster-qwen3-tts --device cuda:0 clone \
  --model Qwen/Qwen3-TTS-12Hz-0.6B-Base \
  --text "Welcome to the workshop." \
  --ref-audio authorized-reference.wav \
  --ref-text "The exact words in that recording." \
  --instruct "Speak warmly and clearly." \
  --language English --output speech.wav
```

`custom` uses a CustomVoice checkpoint and `--speaker`; `design` uses the 1.7B
VoiceDesign checkpoint and `--instruct`. `serve` retains a model while reading
text lines from stdin; the maintained HTTP service is Studio. Use CLI `--help`
for per-command options. GGML/GGUF and CPU inference are not supported.

## Conditioning and streaming

Base cloning defaults to transcript-guided ICL with incremental text feeding.
`xvec_only=True` uses speaker identity without transcript-guided reference
context. Both modes accept delivery direction through the faster wrapper; voice
and delivery quality depend on the checkpoint and reference. Studio caches
prepared references on CPU and lets users export designed voices as references.

`non_streaming_mode=True` prefills the full target text; false feeds trailing
text incrementally during decode. This controls text conditioning independently
of whether audio is streamed. CustomVoice and VoiceDesign default to full-text
conditioning in Studio.

The accelerated path reuses Qwen's model forward passes with fixed-size KV caches
and CUDA graphs for talker/predictor decoding. Graph replay reduces repeated
dispatch overhead. Streaming yields codec chunks and decodes with left context
to reduce boundary artifacts. It uses the same checkpoints as ordinary Qwen
generation; it is not a separately trained model.

## Validation

Docker's `checks` target runs CPU regressions without network access, including
compatibility helpers and fresh Studio startup. GPU tests in
`tests/test_e2e_parity.py` compare local Qwen generation and acceleration.
Cloning tests require `QWEN_TTS_REF_AUDIO` and its exact `QWEN_TTS_REF_TEXT` from
an authorized recording. Do not substitute removed upstream recordings.

The inherited dynamic-cache parity mode is a diagnostic path. Sampled output
and floating-point differences require appropriate comparisons; do not assume
every fast-path waveform will be bit-identical. `task smoke` checks real Studio
audio through an explicitly configured external ASR service and never starts
local ASR. Neither short smoke checks nor the
[historical upstream tables](UPSTREAM_BENCHMARKS.md) qualify product performance.
