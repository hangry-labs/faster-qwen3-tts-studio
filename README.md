# Faster Qwen3-TTS

Real-time Qwen3-TTS inference with streaming and non-streaming generation. The
Torch backend uses `torch.cuda.CUDAGraph`; the GGML backend supports CUDA and
Apple Silicon Metal.

## Development tasks

The Hangry Labs development workflow uses Task, PowerShell 7, uv, and Docker
Desktop with NVIDIA GPU support:

```powershell
task init
task start
# Open http://127.0.0.1:7860
task stop
```

`task nuke` removes this project's container, development image, and persistent
data volume. `task release` validates and builds local Python artifacts;
publication is not configured yet. See [development tasks](docs/DEVELOPMENT.md)
for setup, settings, cache behavior, and validation commands. The development
image uses Python 3.13 and Torch; the upstream installation paths below remain
available separately.

## Install

Requires: Python 3.10+ and PyTorch 2.5.1+. The Torch backend requires
an NVIDIA GPU with CUDA. The GGML backend also runs on Apple Silicon
Macs with macOS 14 or newer.

```bash
pip install faster-qwen3-tts
```

On native Apple Silicon Python, this also installs the GGML Metal runtime and
the CLI selects it automatically. Intel Macs and Rosetta Python are not
supported by the Metal wheel.

The default install uses `qwen-tts-hf`, a temporary PyPI compatibility build
of Qwen3-TTS with Transformers 5 support. It provides the same `qwen_tts`
Python package as upstream `qwen-tts`; do not install both distributions in
the same environment.

**PyTorch compatibility note:** CUDA-graph capture in the fast path is not reliable on `torch<=2.5.0` for this project (capture can fail with "operation not permitted when stream is capturing"). We validated `2.5.1+` as working and set that as the minimum supported version.

**Blackwell note:** RTX 50xx / Blackwell GPUs need CUDA 12.8 PyTorch wheels. If the default setup fails on those cards, install a `cu128` PyTorch build (PyTorch 2.7+).

**Driver / CUDA mismatch note (T4, A10G, and other CUDA-12.4 hosts):** `pip install` pulls the default PyTorch wheel, which is built against a recent CUDA toolkit. If your NVIDIA driver is *older* than that toolkit — common on CUDA 12.4 hosts such as AWS, Azure ML, and many Colab/T4 boxes — `torch.cuda.is_available()` returns `False` with `CUDA initialization: The NVIDIA driver on your system is too old`. Install a PyTorch wheel matching your driver's CUDA version. Check it with `nvidia-smi` (top-right "CUDA Version"); for a CUDA 12.4 driver:

```bash
pip install "torch==2.5.1" "torchaudio==2.5.1" --index-url https://download.pytorch.org/whl/cu124
```

### Experimental GGML backend

There is an experimental adapter for Pascal's `qwentts.cpp` runtime. The CLI
selects Torch when CUDA is available and GGML otherwise. On Apple Silicon,
the native GGML wheel is included in the default install. On other platforms,
install the `ggml` extra to get it. Use `--backend` to choose one explicitly.

The GGML backend uses `log_level="warning"` by default in Python and the CLI,
hiding routine startup and generation diagnostics while keeping warnings, errors,
download progress, and the final `Wrote ...` result visible. Add `--verbose`
before the CLI subcommand or pass `qwentts_log_level="debug"` to
`FasterQwen3TTS.from_pretrained(..., backend="ggml")` to see native diagnostics.

```bash
pip install "faster-qwen3-tts[ggml]"

faster-qwen3-tts --backend ggml --quant BF16 design \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
  --instruct "Warm, confident narrator" \
  --text "Welcome to the show." \
  --language English \
  --output out.wav
```

The extra requires `qwentts-cpp-python>=0.5.0`. The PyPI release provides a
Metal wheel for macOS 14+ with native Apple Silicon Python and CUDA 12.8
wheels for supported Linux hosts. Pip selects the matching wheel. No local
native build or `--qwentts-lib` path is needed on a supported Mac. For other
Linux runtimes, install the matching wrapper wheel from the Hugging Face
wheelhouse before installing the extra. The 0.5.0 wheel variants use the same
ABI v5 as the PyPI release:

```bash
# Ubuntu 22.04 / older Linux with CUDA 12.8
pip install "qwentts-cpp-python==0.5.0+cu128" \
  -f https://huggingface.co/datasets/andito/qwentts-cpp-python-wheels/tree/main/whl/cu128

# CUDA 13 / DGX Spark
pip install "qwentts-cpp-python==0.5.0+cu130" \
  -f https://huggingface.co/datasets/andito/qwentts-cpp-python-wheels/tree/main/whl/cu130

pip install "faster-qwen3-tts[ggml]"
```

See [`docs/ggml-backend.md`](docs/ggml-backend.md) for the native wrapper
package and installation details.

The GGML backend caches raw reference audio as qwentts.cpp `.spk` speaker
latents plus `.rvq` acoustic latents after the first clone request. You can also
pass precomputed references directly:

```bash
faster-qwen3-tts --backend ggml --quant BF16 clone \
  --model Qwen/Qwen3-TTS-12Hz-1.7B-Base \
  --ref-spk freeman.spk \
  --ref-rvq freeman.rvq \
  --ref-text "$(cat freeman.txt)" \
  --text "Cached references skip reference audio encoding on every request." \
  --language English \
  --output out.wav
```

## Quick Start

### Python

```python
from examples.audio import StreamPlayer  # helper from this repo's examples/
from faster_qwen3_tts import FasterQwen3TTS

model = FasterQwen3TTS.from_pretrained("Qwen/Qwen3-TTS-12Hz-0.6B-Base")
ref_audio = "ref_audio.wav"
ref_text = "The exact transcript of your authorized reference recording."

# Streaming — yields audio chunks during generation
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

# Non-streaming — returns all audio at once
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

`examples/audio.py` contains a small `StreamPlayer` helper used by [`examples/streaming_playback.py`](examples/streaming_playback.py). It keeps one output stream open and queues chunks into it. A one-shot player such as `sounddevice.play(audio_chunk, sr)` restarts playback per chunk and can introduce gaps.

### CLI

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

### Demo UI

A minimal web UI that streams audio in real time and shows TTFA and RTF live.
It defaults to GGML/qwentts.cpp and includes a backend toggle for comparing it
against the Torch CUDA-graph backend:

```bash
pip install -e ".[demo,ggml]"
python demo/server.py --backend ggml
# open http://localhost:7860
```

Features: voice clone (upload any WAV or use your microphone), voice design (1.7B-VoiceDesign model), GGML/Torch backend toggle, streaming/non-streaming toggle, adjustable chunk size, live TTFA/RTF metrics, WAV download.

### OpenAI-compatible API server

`examples/openai_server.py` exposes a `POST /v1/audio/speech` endpoint that follows the OpenAI TTS API contract, so it works out of the box with OpenWebUI, llama-swap, and any other OpenAI-compatible client.

```bash
pip install "faster-qwen3-tts[demo]"
python examples/openai_server.py \
    --ref-audio ref_audio.wav \
    --ref-text "The exact transcript of your authorized reference recording." \
    --language English --port 8000
```

```bash
curl http://localhost:8000/v1/audio/speech \
    -H "Content-Type: application/json" \
    -d '{"model": "tts-1", "input": "Hello world.", "voice": "alloy", "response_format": "wav"}' \
    --output speech.wav
```

To expose multiple voices, pass a JSON file mapping names to reference audio configs — each `voice` value in a request will be routed to the matching entry (`--voices voices.json`). WAV and PCM formats stream chunks as they are generated; MP3 requires `pydub`.

## Results

Benchmarks include tokenization + inference (apples-to-apples with baseline). RTF > 1.0 = faster than real-time. TTFA measured as time to first playable audio chunk using streaming (chunk_size=8).

### 0.6B Model

| GPU | Baseline RTF | Baseline TTFA | CUDA Graphs RTF | CUDA Graphs TTFA | Speedup |
|---|---|---|---|---|---|
| Jetson AGX Orin 64GB | 0.179 | 3,641ms | 1.307 | 597ms | 7.3x / 6.1x |
| DGX Spark (GB10) | 1.17 | 567ms | 2.56 | 280ms | 2.2x / 2.0x |
| RTX 4090 | 0.82 | 800ms | **4.78** | **156ms** | 5.8x / 5.1x |
| RTX 4060 (Windows) | 0.23 | 2,697ms | **2.26** | **413ms** | 9.8x / 6.5x |
| H100 80GB HBM3 | 0.435 | 1,474ms | **3.884** | **228ms** | 8.9x / 6.5x |
| Tesla T4 16GB | 0.467 | 1,671ms | **1.068** | **901ms** | 2.3x / 1.9x |

### 1.7B Model

| GPU | Baseline RTF | Baseline TTFA | CUDA Graphs RTF | CUDA Graphs TTFA | Speedup |
|---|---|---|---|---|---|
| Jetson AGX Orin 64GB | 0.183 | 3,573ms | 1.089 | 693ms | 6.0x / 5.2x |
| DGX Spark (GB10) | 1.01 | 661ms | 1.87 | 400ms | 1.9x / 1.7x |
| RTX 4090 | 0.82 | 850ms | **4.22** | **174ms** | 5.1x / 4.9x |
| RTX 4060 (Windows) | 0.23 | 2,905ms | **1.83** | **460ms** | 7.9x / 6.3x |
| H100 80GB HBM3 | 0.439 | 1,525ms | **3.304** | **241ms** | 7.5x / 6.3x |
| Tesla T4 16GB | 0.453 | 1,811ms | **0.925** | **1,096ms** | 2.0x / 1.7x |

**Note:** Baseline TTFA values are **streaming TTFA** from the community `Qwen3-TTS-streaming` fork (which adds streaming) or from our **dynamic-cache parity streaming** path (no CUDA graphs) where available. The official `Qwen3-TTS` repo does **not** currently support streaming, so without a streaming baseline TTFA would be **time-to-full-audio**. CUDA graphs uses `generate_voice_clone_streaming(chunk_size=8)` for TTFA. Both include text tokenization for fair comparison. Speedup shows throughput / TTFA improvement. The streaming fork reports additional speedups that appear tied to `torch.compile`; we couldn’t reproduce those on Jetson-class devices where `torch.compile` isn’t available.

**GPU architecture notes:** RTX 4090 (2.5 GHz clocks) outperforms H100 (1.8 GHz) for single-stream workloads. H100's lower baseline (RTF 0.59 vs 4090's 0.82) reflects design optimization for batch processing rather than single-stream inference.

### Benchmark your hardware

Benchmarks run from source. You only need [uv](https://docs.astral.sh/uv/) and `./setup.sh`:

**Linux / macOS / WSL:**

```bash
git clone https://github.com/andimarafioti/faster-qwen3-tts
cd faster-qwen3-tts
./setup.sh
./benchmark.sh # or ./benchmark.sh 0.6B or ./benchmark.sh 1.7B for a single model
```

**Windows (Native):**

```cmd
git clone https://github.com/andimarafioti/faster-qwen3-tts
cd faster-qwen3-tts
setup_windows.bat
benchmark_windows.bat   # or benchmark_windows.bat 0.6B / 1.7B / both
```

Results are saved as `bench_results_<GPU_NAME>.json` and audio samples as `sample_0.6B.wav` / `sample_1.7B.wav`.

## Streaming

CUDA graphs support streaming output — audio chunks are yielded during generation with the same per-step performance as non-streaming mode.

### Chunk size vs performance (Jetson AGX Orin, 0.6B)

| chunk_size | TTFA | RTF | Audio per chunk |
|---|---|---|---|
| 1 | 240ms | 0.750 | 83ms |
| 2 | 266ms | 1.042 | 167ms |
| 4 | 362ms | 1.251 | 333ms |
| 8 | 556ms | 1.384 | 667ms |
| 12 | 753ms | 1.449 | 1000ms |
| Non-streaming | — | 1.57 | all at once |

Smaller chunks = lower latency but more decode overhead. `chunk_size=2` is the smallest that stays real-time on Jetson.

**Model seed:** All the different model modes are effectively the same speed. The first time you clone a voice, it takes longer, but later it's cached. Use `benchmarks/compare_modes.py` to reproduce. Example on 0.6B, `chunk_size=8`:

| Mode | TTFA (ms) | RTF | ms/step |
| ---- | --------- | --- | ------- |
| VoiceClone xvec | 152 ± 11 | 5.470 ± 0.032 | 15.2 ± 0.1 |
| VoiceClone full ICL | 149 ± 1 | 5.497 ± 0.026 | 15.2 ± 0.1 |
| CustomVoice | 148 ± 1 | 5.537 ± 0.020 | 15.0 ± 0.1 |

### How streaming works

The CUDA graphs are unchanged — both predictor and talker graphs are replayed per step. The streaming generator yields codec ID chunks every `chunk_size` steps, and the model wrapper decodes each chunk to audio using a sliding window with 25-frame left context (matching the upstream codec's `chunked_decode` pattern) to avoid boundary artifacts.

The Python streaming methods are pull-based generators: they prepare the next chunk when the caller requests it. For realtime local playback, use a queue-backed player such as `StreamPlayer`; blocking after each yielded chunk prevents generation and playback from overlapping.

## Voice Cloning Quality

### Cloning modes

`generate_voice_clone` exposes two modes via `xvec_only`:

| Mode | `xvec_only` | Notes |
|---|---|---|
| Simple (x-vector) | `True` | Speaker embedding only — shorter prefill, clean language switching, no `ref_text` needed |
| Advanced (ICL) | `False` (default) | Full reference audio in context — requires accurate `ref_text`, may produce a brief artifact at the start since it literally continues the sentence `ref_wav` you use |

The default now matches upstream Qwen3-TTS: ICL mode with the reference audio in context. X-vector-only mode remains available as an opt-in for cleaner language switching and shorter prefills.

### Decoder context (ICL mode)

The 12 Hz codec uses a causal `chunked_decode`: each frame is reconstructed using prior frames as acoustic context. In ICL mode the reference audio codec tokens are prepended to the generated tokens before decoding, then the reference portion is trimmed from the output. Without this, the codec decoder starts cold with no voice context — the model generates the right tokens but they get reconstructed in the wrong voice. This is handled automatically.

### Text input streaming vs Non-streaming quality

The original Qwen3TTS implementation supports two mode of generation. It either takes the full input text and prepares the utterance, or it feeds the text progressively. This is the `non_streaming_mode` parameter in the generation methods. The name is maintained from the Qwen3TTS implementation, but I understand it might bring some headaches since here we also have general audio output streaming.
The public API uses `non_streaming_mode=None` as a sentinel, which preserves each method's upstream default unless you override it explicitly.
`generate_voice_clone` and `generate_voice_clone_streaming` resolve `None` to `False`, matching upstream step-by-step text feeding during decode.
`generate_custom_voice`, `generate_custom_voice_streaming`, `generate_voice_design`, and `generate_voice_design_streaming` resolve `None` to `True`, matching the upstream CustomVoice and VoiceDesign defaults.
The GGML backend currently has no qwentts.cpp ABI switch for step-by-step text feeding; passing `non_streaming_mode=False` emits a warning and qwentts.cpp uses its native prompt layout.

**Performance impact (RTX 4090, 1.7B, ICL, chunk_size=8):** TTFA is unchanged (≈159ms ± 1ms), and RTF is effectively the same (nsm=False: 4.87 ± 0.01, nsm=True: 4.85 ± 0.01).

### Base-model instruct

`instruct` is available on Base voice cloning, but treat it as experimental when used with `xvec_only=True`. In local testing and upstream-core probing, instruction-following behaved much more predictably in ICL mode (`xvec_only=False`) than in x-vector-only mode.

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

See [the licensing audit](docs/LICENSING.md) for model redistribution and
commercial-use findings. A passing model license does not grant rights to
somebody else's recording or identity.

## Parity

We maintain parity with upstream Qwen3‑TTS in two layers, and document where (and why) the fast path can differ numerically. When we say **Qwen3TTS vs FasterQwen3TTS**, we are comparing the upstream dynamic‑cache path against our static‑cache CUDA‑graph path.

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

A single step involves ~500 small CUDA kernel launches with Python overhead between them. The GPU spends more time waiting for the next kernel than computing.

CUDA graphs capture the entire decode step and replay it as a single GPU operation:

1. **Static KV cache**: pre-allocated fixed-size tensors (no dynamic allocation)
2. **Model's own forward**: SDPA + RoPE via the model's native attention layers
3. **Graph capture**: `torch.cuda.CUDAGraph` for both predictor and talker
4. **Padded attention**: attention mask handles variable-length KV within fixed buffers

### Per-component breakdown (Jetson AGX Orin, 0.6B)

| Component | Before | After |
|---|---|---|
| Talker (28 layers) | 75ms | 12ms |
| Predictor (15 steps) | 190ms | 26ms |
| Overhead | 65ms | 16ms |
| **Total per step** | **330ms** | **54ms** |

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

The speaker embedding is a 4KB file (2048-dim bf16 vector). In `x_vector_only` mode:
- **No accent bleed**: native pronunciation per language
- **Shorter prefill**: 10 tokens vs ~80+ in full ICL clone mode
- **No ref audio at runtime**: just the 4KB embedding file

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

## License

Original wrapper code is MIT licensed. Adapted Qwen/streaming portions retain
Apache-2.0 obligations, so the Python source distribution is described as
`MIT AND Apache-2.0`. Model weights, dependencies, and Docker runtime components
retain their own terms. Read [NOTICE](NOTICE),
[Third-Party Notices](THIRD_PARTY_NOTICES.md), and [the audit](docs/LICENSING.md).

## Responsible use and privacy

Use cloning references only with the necessary recording rights and speaker
authorization. Do not use synthetic voices for deceptive impersonation. Review
the text and audio before publication, including commercial use. The software
can run locally; model downloads and the inherited demo's optional Hugging Face
login are separate network interactions. Do not assume that the current demo
is an offline-qualified Hangry Labs image.

## Acknowledgments

- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) by the Qwen team
- [Qwen3-TTS-streaming](https://github.com/dffdeeq/Qwen3-TTS-streaming) for ideas and code we adapted for streaming
- [nano-qwen3tts-vllm](https://github.com/tsdocode/nano-qwen3tts-vllm) for inspiration on CUDA graph usage
- NVIDIA for providing the Jetson AGX Orin board
