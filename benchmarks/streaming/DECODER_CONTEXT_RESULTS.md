# Streaming decoder context: 25 versus 100 frames

Measured 2026-10-26 on an NVIDIA GeForce RTX 5070 Ti (16 GB), Torch
2.10.0+cu128, Transformers 5.15.1 and BF16. **Keep the default at 25 frames.**
The 100-frame option remains available when a particular voice benefits from
more acoustic context; these measurements do not establish a general audible
quality improvement.

## Resident generation results

Realtime speed is audio seconds divided by generation wall seconds; higher is
faster. Each checkpoint has 12 measured requests per context. Model loading,
graph capture and prompt warmups are excluded.

| Checkpoint | Realtime, 25 | Realtime, 100 | Speed change | Peak allocated, 25 / 100 (MiB) | Peak reserved, 25 / 100 (MiB) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.6B Base | 3.062× | 2.870× | −6.28% | 2628.6 / 2797.5 | 3050 / 4066 |
| 0.6B CustomVoice | 3.062× | 2.874× | −6.15% | 2413.7 / 2590.1 | 2562 / 3156 |
| 1.7B Base | 2.850× | 2.561× | −10.14% | 4569.5 / 4738.4 | 4994 / 6094 |
| 1.7B CustomVoice | 2.812× | 2.694× | −4.20% | 4349.1 / 4525.5 | 4500 / 5094 |
| 1.7B VoiceDesign | 2.865× | 2.629× | −8.25% | 4353.9 / 4530.3 | 4506 / 5100 |

Peak live tensor memory increased by **168.9–176.4 MiB**. The caching allocator's
reserved-memory peak increased by **594–1100 MiB**, which matters when serving
other models. These are Torch allocation/reservation peaks, not whole-device
VRAM readings, and they must not be added together.

Both counterbalanced passes showed a slowdown at 100 frames. Their speed-change
ranges were −7.05% to −5.49% for 0.6B Base, −7.95% to −4.37% for 0.6B CustomVoice,
−11.01% to −9.23% for 1.7B Base, −4.47% to −3.92% for 1.7B CustomVoice, and
−8.60% to −7.90% for VoiceDesign. These are observed pass ranges, not confidence
intervals or a prediction for every workload.

| Checkpoint | Median first decoded chunk, 25 (ms) | At 100 (ms) |
| --- | ---: | ---: |
| 0.6B Base | 290.5 | 275.8 |
| 0.6B CustomVoice | 268.9 | 268.5 |
| 1.7B Base | 295.1 | 309.3 |
| 1.7B CustomVoice | 289.9 | 284.2 |
| 1.7B VoiceDesign | 284.1 | 294.0 |

There is no consistent first-chunk advantage. Context 100 does not require
waiting for 100 frames before the first chunk. These times exclude encoding,
HTTP delivery and browser playback, so they are not time to first audible sound.

## Controls and quality evidence

The experiment completed **120 measured generations**, covering all five
checkpoints, short English, long English and long Japanese. Every one of the
30 matched prompt/seed cases had identical codec tokens and audio length across
both contexts and both passes. All long cases exceeded 100 frames; the shortest
long case contained 213 frames. Every measured generation ended at EOS.

A separate remote-ASR check covered 30 paired recordings. Normalized transcripts
matched between contexts in 14 of 15 pairs. The remaining Japanese pair used
hiragana versus kanji for the same verb (`たたいて` / `叩いて`). These checks do
not demonstrate smoother boundaries, better voice identity or improved naturalness.
No human listening verdict is claimed; generated paired recordings are retained
with each local run for listening.

## Reproduce

Use a current product image and a populated model cache, with other GPU workloads
stopped. Run `task stop`, then `task benchmark-decoder-context`, then `task start`.
Use the same `IMAGE` value for your build and benchmark. Optional arguments:
`task benchmark-decoder-context -- -Models 0.6B-CustomVoice -Repeats 2`.

Each model/context runs in a fresh process with its weights and graphs resident
throughout that worker's measurements. The order is 25, 100, 100, 25, with three
prompt warmups per worker and two measured seeds per prompt. The larger window
therefore cannot inflate the smaller window's allocator history. All contexts
use eight-frame output chunks, the same sampling settings and a 600-token budget.
Cloning uses one fixed, generated English reference and its transcript.

The benchmark runs offline against read-only cached weights. It records raw
JSON, paired WAV examples, actual codec checksums, first-chunk and inter-chunk
timing, allocated/reserved memory and an automatic `RESULTS.md` beneath
`benchmark-artifacts/decoder-context/`. Checksumming adds the same small CPU copy
to both variants. Audio encoding, effects, queueing and network time are excluded.
The measurements describe this workload and hardware, not a universal speed or
quality claim. See [the benchmark guide](../README.md).
