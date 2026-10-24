# Engine and Python reference

The supported Hangry Labs product path is the [NVIDIA Docker Studio](../README.md).
This secondary guide retains the inherited Python/CLI interfaces and explains
the generation engine. Run examples from the repository root in a compatible
inference environment. The development image uses Python 3.13 and pinned core
Torch/CUDA wheels; see [development setup](DEVELOPMENT.md).

The `qwen-tts-hf` dependency supplies the `qwen_tts` import package. Do not install
it alongside the upstream `qwen-tts` distribution in the same environment.

## Python

```python
from examples.audio import StreamPlayer  # helper from this repo's examples/
from faster_qwen3_tts import FasterQwen3TTS

model = FasterQwen3TTS.from_pretrained("Qwen/Qwen3-TTS-12Hz-0.6B-Base")
ref_audio = "ref_audio.wav"
ref_text = "The exact transcript of your authorized reference recording."

# Streaming - yields audio chunks during generation
play = StreamPlayer()
try:
    for audio_chunk, sr, timing in model.generate_voice_clone_streaming(
        text="What do you mean that I'm not real?", language="English",
        ref_audio=ref_audio, ref_text=ref_text,
        chunk_size=8,  # 8 steps ≈ 667ms of audio per chunk
    ):
        play(audio_chunk, sr)
finally:
    play.close()

# Non-streaming - returns all audio at once
audio_list, sr = model.generate_voice_clone(
    text="Hello world!", language="English",
    ref_audio=ref_audio, ref_text=ref_text,
)
```

Call `model.warmup(prefill_len=100)` to prepare a model explicitly before
serving requests. It captures CUDA graphs for the Torch backend and is a safe
no-op for GGML; normal generation also performs any required lazy preparation.

For local speaker playback from a repo checkout with the example helper:

```bash
pip install sounddevice
```

`examples/audio.py` contains a small `StreamPlayer` helper used by [`examples/streaming_playback.py`](../examples/streaming_playback.py). It keeps one output stream open and queues chunks into it. A one-shot player such as `sounddevice.play(audio_chunk, sr)` restarts playback per chunk and can introduce gaps.

## CLI

Voice cloning (reference audio):

```bash
faster-qwen3-tts clone \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-Base \
  --text "What do you mean that I'm not real?" \
  --language English \
  --ref-audio ref_audio.wav \
  --ref-text "The exact transcript of your authorized reference recording." \
  --output out.wav
```

CustomVoice (predefined speaker IDs):

```bash
faster-qwen3-tts custom --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --list-speakers
faster-qwen3-tts custom \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice \
  --speaker aiden \
  --text "What do you mean that I'm not real?" \
  --language English \
  --output out.wav
```

VoiceDesign (instruction-based):

```bash
faster-qwen3-tts design \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
  --instruct "Warm, confident narrator with slight British accent" \
  --text "Welcome to the show." \
  --language English \
  --output out.wav
```

Streaming generation to a final WAV file (prints RTF after write):

```bash
faster-qwen3-tts custom \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice \
  --speaker aiden \
  --text "What do you mean that I'm not real?" \
  --language English \
  --output out.wav \
  --streaming
```

Server mode (keep model hot, stop with `exit`):

```bash
faster-qwen3-tts serve \
  --mode custom \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice \
  --speaker aiden \
  --language English \
  --streaming
```

## Streaming internals

Audio streaming yields playable chunks during generation. Chunk size trades
first-audio latency against decoding overhead; see the
[inherited measurements](UPSTREAM_BENCHMARKS.md) for historical examples.

### How streaming works

The CUDA graphs are unchanged - both predictor and talker graphs are replayed per step. The streaming generator yields codec ID chunks every `chunk_size` steps, and the model wrapper decodes each chunk to audio using a sliding window with 25-frame left context (matching the upstream codec's `chunked_decode` pattern) to avoid boundary artifacts.

The Python streaming methods are pull-based generators: they prepare the next chunk when the caller requests it. For realtime local playback, use a queue-backed player such as `StreamPlayer`; blocking after each yielded chunk prevents generation and playback from overlapping.

## Voice Cloning Quality

### Cloning modes

`generate_voice_clone` exposes two modes via `xvec_only`:

| Mode | `xvec_only` | Notes |
|---|---|---|
| Simple (x-vector) | `True` | Speaker embedding only - shorter prefill, clean language switching, no `ref_text` needed |
| Advanced (ICL) | `False` (default) | Full reference audio in context - requires accurate `ref_text`, may produce a brief artifact at the start since it literally continues the sentence `ref_wav` you use |

The default now matches upstream Qwen3-TTS: ICL mode with the reference audio in context. X-vector-only mode remains available as an opt-in for cleaner language switching and shorter prefills.

### Decoder context (ICL mode)

The 12 Hz codec uses a causal `chunked_decode`: each frame is reconstructed using prior frames as acoustic context. In ICL mode the reference audio codec tokens are prepended to the generated tokens before decoding, then the reference portion is trimmed from the output. Without this, the codec decoder starts cold with no voice context - the model generates the right tokens but they get reconstructed in the wrong voice. This is handled automatically.

### Text input streaming vs Non-streaming quality

Qwen can receive the whole input text before generation or receive it
progressively. The inherited `non_streaming_mode` parameter controls text input;
it is independent of streaming audio output.
The public API uses `non_streaming_mode=None` as a sentinel, which preserves each method's upstream default unless you override it explicitly.
`generate_voice_clone` and `generate_voice_clone_streaming` resolve `None` to `False`, matching upstream step-by-step text feeding during decode.
`generate_custom_voice`, `generate_custom_voice_streaming`, `generate_voice_design`, and `generate_voice_design_streaming` resolve `None` to `True`, matching the upstream CustomVoice and VoiceDesign defaults.
The GGML backend currently has no qwentts.cpp ABI switch for step-by-step text feeding; passing `non_streaming_mode=False` emits a warning and qwentts.cpp uses its native prompt layout.

Historical performance figures are kept in the [upstream benchmark reference](UPSTREAM_BENCHMARKS.md); they are not measurements of this Studio build.

### Base-model instruct

`instruct` is forwarded in complete and streaming Base cloning. Instruction following is experimental. Transcript-assisted ICL (`xvec_only=False`) is recommended; identity-only mode may ignore direction. This is not the same instruction-control qualification as 1.7B CustomVoice.

### ICL Phoneme Artifact

In ICL mode the model's prefill ends with the last codec token of the reference audio, so the first generated token is conditioned on whatever phoneme the reference ends on. If the reference ends mid-word, that phoneme bleeds into the generated speech.

**The fix is applied by default.** The wrapper appends 0.5 s of silence to the reference audio before encoding it, giving the model a clean starting point regardless of how the recording ends. Set `append_silence=False` to match the upstream behavior exactly.

## Reference recordings and validation

Supply reference audio that you have permission to process and clone, with an
accurate transcript for ICL mode. The inherited reference recordings and audio
comparisons were removed because their media provenance was not established.
They are not included in current packages or images.

For real-model cloning tests, set `QWEN_TTS_REF_AUDIO` to your recording and
`QWEN_TTS_REF_TEXT` to its exact transcript. Cloning fixtures skip when those
inputs are unavailable. CustomVoice and VoiceDesign tests do not need an
external reference recording.

See [the licensing audit](LICENSING.md) for model redistribution and
commercial-use findings. A passing model license does not grant rights to
somebody else's recording or identity.

## Parity

The inherited parity suite compares the upstream dynamic-cache path with the static-cache CUDA-graph path. These GPU/model tests are separate from ordinary CPU unit tests and Studio smoke checks; passing those checks does not mean this full parity suite has run.

- **Fast path (static cache + CUDA graphs):** Streaming and non‑streaming share the same decode core and match upstream for the initial window where artifacts are most audible. Tests enforce this prefix parity deterministically.
- **Parity mode (dynamic cache, tests only):** A dynamic‑cache decode path (no CUDA graphs) that calls `talker.generate(...)` is used in tests to prove exact token‑level equality against upstream for all model types.

**Why can static cache differ from dynamic cache?** The math is equivalent, but the kernel path is not. Static cache uses a fixed max‑length KV buffer and an explicit attention mask, which often selects a different SDPA kernel than the dynamic cache path (shorter K/V, `is_causal=True`, mask‑free). In BF16/TF32, different kernel/reduction orders are not bit‑exact, so the outputs can differ slightly even when the algorithm is the same.

**Parity streaming note:** The dynamic‑cache parity streaming path is intentionally slow. On an RTX 4090 it measured ~0.77s TTFA (chunk_size=8) and ~1.17s TTFA (chunk_size=12), versus ~0.16–0.18s TTFA in the fast CUDA‑graph path. Use parity streaming only for validation, not performance.

Tests live in `tests/test_e2e_parity.py` and cover:

- Voice clone (x‑vector) prefix parity vs upstream
- Streaming vs non‑streaming parity (fast path)
- CustomVoice full equality (parity mode)
- VoiceDesign full equality (parity mode)
- Voice clone ICL full equality (parity mode)

You can control the model IDs used by tests via environment variables:

```
QWEN_TTS_MODEL=Qwen/Qwen3-TTS-12Hz-0.6B-Base
QWEN_TTS_CUSTOM_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
QWEN_TTS_VOICE_DESIGN_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

## How It Works

Qwen3-TTS runs two autoregressive transformers per decode step:
1. **Talker** (28 layers): generates the first codebook token from text
2. **Code Predictor** (5 layers): generates 15 additional codebook tokens

Autoregressive decoding dispatches many small operations. CUDA graph replay reduces repeated Python dispatch overhead.

CUDA graphs capture the entire decode step and replay it as a single GPU operation:

1. **Static KV cache**: pre-allocated fixed-size tensors (no dynamic allocation)
2. **Model's own forward**: SDPA + RoPE via the model's native attention layers
3. **Graph capture**: `torch.cuda.CUDAGraph` for both predictor and talker
4. **Padded attention**: attention mask handles variable-length KV within fixed buffers

## Voice Cloning with Precomputed Speaker Embeddings

For production use, extract the speaker embedding once and reuse it:

```bash
# 1. Extract speaker embedding from reference audio (one-time, ~10s)
python examples/extract_speaker.py --ref_audio voice.wav --output speaker.pt

# 2. Generate speech with CUDA graphs (real-time)
python examples/generate_with_embedding.py --speaker speaker.pt --text "Hello!" --language English --output en.wav
python examples/generate_with_embedding.py --speaker speaker.pt --text "Bonjour!" --language French --output fr.wav
python examples/generate_with_embedding.py --speaker speaker.pt --text "Hallo!" --language German --output de.wav
```

Identity-only conditioning can reuse a saved speaker embedding without reopening
the reference recording. It omits the reference's transcript and acoustic-token
context; pronunciation and language quality still depend on the model and input.

You can now pass a precomputed prompt directly to the public APIs. The wrapper
accepts either:
- the raw `prompt_items` list returned by `create_voice_clone_prompt(...)`
- or the lower-level dict form produced by `_prompt_items_to_voice_clone_prompt(...)`

```python
import torch
from faster_qwen3_tts import FasterQwen3TTS

model = FasterQwen3TTS.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base")

# 1) Compute prompt_items once from reference audio
prompt_items = model.model.create_voice_clone_prompt(
    ref_audio="voice.wav",
    ref_text="",
    x_vector_only_mode=True,
)

# 2) You can pass prompt_items directly
audio_list, sr = model.generate_voice_clone(
    text="Hello world!",
    language="English",
    voice_clone_prompt=prompt_items,
)

# 3) Or save just the speaker embedding and rebuild the compact dict form
spk_emb = prompt_items[0].ref_spk_embedding

torch.save(spk_emb.detach().cpu(), "speaker.pt")

spk_emb = torch.load("speaker.pt", weights_only=True).to(model.device)

voice_clone_prompt = {
    "ref_spk_embedding": [spk_emb],
}

audio_list, sr = model.generate_voice_clone(
    text="Hello world!",
    language="English",
    voice_clone_prompt=voice_clone_prompt,
)
```

When `voice_clone_prompt` is provided, prompt extraction from `ref_audio` is skipped.
For x-vector-only prompts, `ref_text` is ignored.
For ICL precomputed prompts, pass `x_vector_only_mode=[False]`, `icl_mode=[True]`,
and a non-`None` `ref_code`, and keep `ref_text` populated.

## Other inherited interfaces

- [GGML adapter reference](ggml-backend.md): experimental engine support, outside
  the NVIDIA/Torch Studio target.
- [Separate OpenAI server example](../examples/openai_server.py): an inherited
  standalone example, not a route served by the Studio Docker command. Qualify
  it independently before integrating it into an application.
- [Original engine notes](../BLOG.md): historical explanation of the optimization.

The engine reuses the official Qwen model checkpoints. CUDA graph acceleration
changes inference execution; it does not provide a separate set of Faster Qwen
model weights.
