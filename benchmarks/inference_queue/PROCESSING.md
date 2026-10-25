# Concurrent processing experiment

GPU: NVIDIA GeForce RTX 5070 Ti (16303 MiB), driver 610.88.

4 concurrent clients, 5 paired rounds per workload and image. Sequential and queued order alternates each round; fixed seeds and WAV output. Each isolated worker loads one checkpoint and discards its warmup. All measured model-load times are zero. Other containers remain untouched.

Sampling: temperature 0.9, top-k 50, repetition penalty 1.05, token cap 600, chunk size 8. GPU telemetry requested every 0.1 s.

Plain is the existing speech control. Processed is two SSML turns with rate/pitch/volume effects, a 120 ms break and whole-recording loudness normalization. Gains below compare the same submission mode across images. They do not compare sequential submission against queued submission. Before/after labels denote code versions; run IDs show execution order. Repeating the baseline image after the candidate helps check drift.

| Workload | Submission | Before s | After s | Throughput change | Round change range |
| --- | --- | ---: | ---: | ---: | ---: |
| plain | sequential | 80.578 | 79.946 | +0.79% | -4.47% to +9.07% |
| plain | queued | 79.598 | 80.847 | -1.55% | -8.79% to +3.73% |
| processed | sequential | 48.947 | 47.769 | +2.47% | +0.70% to +5.57% |
| processed | queued | 48.890 | 45.680 | +7.03% | +4.16% to +8.51% |

Round ranges show observed variation, not confidence intervals. These are short complete-response workloads on one GPU; results do not establish a general speedup for every text, checkpoint, clone reference or streaming format. VRAM figures include the variable desktop baseline. RAM is the container high-water mark, including file-cache accounting. These figures do not establish an allocator-memory improvement.

| Workload | Queued median latency before / after s | Queued p95 before / after s | GPU peak before / after MiB | RAM peak before / after MiB | Identical WAVs per mode |
| --- | ---: | ---: | ---: | ---: | ---: |
| plain | 10.304 / 10.213 | 17.144 / 16.643 | 6550 / 6301 | 2575.2 / 2577.0 | 20 |
| processed | 6.244 / 5.646 | 9.960 / 9.265 | 5556 / 5793 | 2527.5 / 2541.4 | 20 |

## plain: Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice

Before run `20261025-124953-c490cf00`; after run `20261025-124353-a6324bc9`.

Before image `sha256:6dcc3ddcd3203a8a84b0c391f1b568b14d93a4aa396aa8b08d1e24cbf5f571f3`; after image `sha256:c788fad342898335b9d6f76fa4ff200c5117cc06c187cd890e3b006881fff7d6`.

Inference source hashes: `a439964836205203eca9f608ffe3b7e179d4627628f49ca806aef534b5e1259b` and `812c76c465b996215abcc326034688765e31c704beb98a41c7616afbd822edec`.

After: mean queued GPU lease 3864.330 ms; mean CPU tail 0.060 ms. The lease includes model-side preparation, inference and codec decoding. The CPU tail can overlap the next request; HTTP encoding is measured only by client latency.

## processed: Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice

Before run `20261025-125257-551adb37`; after run `20261025-124752-481c8760`.

Before image `sha256:6dcc3ddcd3203a8a84b0c391f1b568b14d93a4aa396aa8b08d1e24cbf5f571f3`; after image `sha256:c788fad342898335b9d6f76fa4ff200c5117cc06c187cd890e3b006881fff7d6`.

Inference source hashes: `a439964836205203eca9f608ffe3b7e179d4627628f49ca806aef534b5e1259b` and `812c76c465b996215abcc326034688765e31c704beb98a41c7616afbd822edec`.

After: mean queued GPU lease 2129.213 ms; mean CPU tail 191.027 ms. The lease includes model-side preparation, inference and codec decoding. The CPU tail can overlap the next request; HTTP encoding is measured only by client latency.
