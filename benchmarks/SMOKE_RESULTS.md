# Preliminary GPU smoke, 2026-10-25

All five manual smoke suites ran on a **shared GPU**, with one measured repeat
or paired round per scenario. These are wiring and capability checks, not a
controlled multilingual performance baseline or a release qualification.
Warmups and model loading were excluded from warmed timings. All results
were retained locally with `--no-write --allow-shared-gpu`; official histories
and per-suite benchmark reports were not promoted.

Hardware: NVIDIA GeForce RTX 5070 Ti, 16303 MiB, NVIDIA driver 610.88.
Runtime: Python 3.13.17, Torch 2.10.0+cu128, Transformers 5.15.1.
Judge: remote `Qwen/Qwen3-ASR-0.6B-hf`. No local ASR model ran.

## Coverage

| Suite | Measured requests | Result |
| --- | ---: | --- |
| baseline | 6 | Pass |
| backends | 8 | Pass |
| streaming | 6 | Pass |
| ssml | 4 | Pass |
| queue | 16 | Pass |

40 measured requests, plus discarded warmups. English covers built-in voices,
reference cloning and description-based design. The four-scenario pilot also
covers Japanese VoiceDesign. Queue checks use four concurrent clients.

## Warmed complete generation

One English request per engine and checkpoint. RTF is client wall time divided
by generated audio duration; lower is faster. Generated durations can differ.

| Checkpoint | Native RTF | Faster RTF | Faster realtime speed (×) |
| --- | ---: | ---: | ---: |
| 0.6B-CustomVoice | 2.060 | 0.317 | 3.15x |
| 0.6B-Base | 1.935 | 0.304 | 3.29x |
| 1.7B-VoiceDesign | 1.964 | 0.346 | 2.89x |

All six complete-generation samples matched the expected transcript after
normalization. Short baseline, pilot and streaming samples had 99.6 to 100%
ASR similarity overall. This checks spoken words, not naturalness, expression
or speaker identity.

## First streamed audio

Client time to the first decoded nonempty audio event, with chunk size 8.
Native inference emits one completed waveform and is explicitly buffered.

| Checkpoint | Native buffered first audio, ms | Faster incremental first audio, ms |
| --- | ---: | ---: |
| 0.6B-CustomVoice | 11186 | 297 |
| 0.6B-Base | 18488 | 324 |
| 1.7B-VoiceDesign | 8447 | 362 |

## Ten-turn dialogue

Standard SSML and SSML-H use the same ten-turn corpus. SSML-H additionally
supplies delivery directions, requiring 1.7B CustomVoice for this built-in
speaker comparison. Each measured document passed all ten ordered ending
markers and the final-tail check.

| Engine | Input | TTS seconds | Audio seconds | ASR similarity |
| --- | --- | ---: | ---: | ---: |
| native | ssml | 111.35 | 54.08 | 99.73% |
| native | ssml-h | 127.16 | 53.50 | 100.00% |
| faster | ssml | 20.68 | 53.01 | 100.00% |
| faster | ssml-h | 20.73 | 56.50 | 100.00% |

## Four-client FIFO

One round submits the same four fixed-seed requests sequentially and then
concurrently. A queued request includes its waiting time. This is an integrity
and scheduling check, not a claim of parallel model inference.

| Engine | Identical paired WAVs | Peak waiting requests | Sequential batch, s | Queued batch, s |
| --- | ---: | ---: | ---: | ---: |
| native | 4/4 | 3 | 117.44 | 114.97 |
| faster | 4/4 | 3 | 14.70 | 14.98 |

## Reproducibility and limits

Follow-up residency checks exercised the packaged Studio with all three defaults
loaded together: 0.6B Base, 0.6B CustomVoice and 1.7B VoiceDesign. Each workflow
generated valid speech with 0 ms model-loading time and exact normalized ASR.
Request-only CustomVoice reloaded on successive requests. Disabling residency
released all weights and graph resources; the process reported **0 MiB allocated
and 0 MiB reserved** through PyTorch. Re-enabling residency restored all defaults.
These functional checks are separate from the 40 measured smoke requests above.

The follow-up fixed teardown of captured graphs and cached cuBLAS workspaces.
Workspace cleanup runs only after all models and graphs have been disposed, so
remaining pinned graphs keep valid buffers. See the
[pinned PyTorch CUDA notes](https://github.com/pytorch/pytorch/blob/v2.10.0/docs/source/notes/cuda.rst#cublas-workspaces).

Regular baseline and streaming commands default to preloaded 0.6B Base and
CustomVoice. This smoke explicitly added 1.7B VoiceDesign, the only design
checkpoint. Each isolated worker kept its measured checkpoint resident.
The native adapter uses local standard inference; Faster uses the accelerated
production engine. Both use the same planner, pinned catalog, seed handling
and output paths. Device VRAM includes unrelated workloads and display memory.
No repeated-run confidence intervals or full ten-language baseline are claimed.

Tested local benchmark image: `sha256:2ef145ee51915dd32c64c70272c1b3e0f94c288875d2d17f08f5c58617059117`.
Installed source SHA-256: `edfb7dcccba6d67736813f9f85d188fbb45a4a406d26e79f2a338465f5aa876e`.

| Suite | Local run id |
| --- | --- |
| baseline | `20261025-033558-773405b0` |
| backends | `20261025-033856-dec471ff` |
| streaming | `20261025-034400-02bcbf67` |
| ssml | `20261025-034802-a7779784` |
| queue | `20261025-035857-a6bbfa2a` |

See the [suite guide](README.md) for the measurement contract and commands.
`task benchmark-smoke -- --allow-shared-gpu` runs all five smoke suites;
select 1.7B VoiceDesign explicitly in the individual baseline/streaming tasks
to include the extra design profiles shown here. Keep raw recordings local.
