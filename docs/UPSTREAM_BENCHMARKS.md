# Inherited Faster Qwen3-TTS benchmarks

These tables are retained from the upstream-derived README for reference. They
are upstream measurements, not Hangry Labs Studio benchmarks or hardware
requirements. They have not been reproduced against this fork's current Python
3.13 development image. Model settings, warmup, reference preparation, GPU load
and client playback affect results; do not compare unlike measurements directly.

The Studio's GPU smoke checks verify generation and transcription correctness.
They do not qualify perceptual quality, representative latency or capacity.
See the [Studio guide](STUDIO.md) for timing definitions and the
[original engine](https://github.com/andimarafioti/faster-qwen3-tts) for context.

## Results

Upstream reports tokenization plus inference. Its tables use **RTF** to mean
audio seconds per generation second, so larger values are faster. This is the
reciprocal of the generation-time/audio-duration convention sometimes called
real-time factor. TTFA is time to first playable chunk with `chunk_size=8`.

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

Baseline TTFA here comes from the community streaming fork or the inherited
dynamic-cache parity streaming path, where available. These historical baselines
should not be confused with a measurement of the official non-streaming call's
time to full audio. Speedup columns list throughput improvement followed by
first-audio improvement. These timings do not include the Studio's browser
receipt and scheduled-playback measurements.

### Chunk size vs performance (Jetson AGX Orin, 0.6B)

| chunk_size | TTFA | RTF | Audio per chunk |
|---|---|---|---|
| 1 | 240ms | 0.750 | 83ms |
| 2 | 266ms | 1.042 | 167ms |
| 4 | 362ms | 1.251 | 333ms |
| 8 | 556ms | 1.384 | 667ms |
| 12 | 753ms | 1.449 | 1000ms |
| Non-streaming | - | 1.57 | all at once |

Smaller chunks = lower latency but more decode overhead. `chunk_size=2` is the smallest that stays real-time on Jetson.

**Model seed:** The inherited comparison below reports similar speeds for its tested model modes. The first time you clone a voice, it takes longer, but later it's cached. Use `benchmarks/compare_modes.py` to reproduce. Example on 0.6B, `chunk_size=8`:

| Mode | TTFA (ms) | RTF | ms/step |
| ---- | --------- | --- | ------- |
| VoiceClone xvec | 152 ± 11 | 5.470 ± 0.032 | 15.2 ± 0.1 |
| VoiceClone full ICL | 149 ± 1 | 5.497 ± 0.026 | 15.2 ± 0.1 |
| CustomVoice | 148 ± 1 | 5.537 ± 0.020 | 15.0 ± 0.1 |

### Per-component breakdown (Jetson AGX Orin, 0.6B)

| Component | Before | After |
|---|---|---|
| Talker (28 layers) | 75ms | 12ms |
| Predictor (15 steps) | 190ms | 26ms |
| Overhead | 65ms | 16ms |
| **Total per step** | **330ms** | **54ms** |

## Benchmark tooling

Research scripts remain under `benchmarks/` and in the root benchmark helpers.
They are separate from the maintained Studio workflow and may need their own
dependencies or GPU allocations. Optional Parakeet utilities are not part of
the default image or Studio tests. Do not start a local ASR model when using an
existing transcription service for Studio checks.
