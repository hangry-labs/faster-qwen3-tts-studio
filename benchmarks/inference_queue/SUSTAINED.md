# Sustained concurrent inference

GPU: NVIDIA GeForce RTX 5070 Ti, 16303 MiB; driver 610.88.

Checkpoint: `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`. 90-second steady windows, 2 passes at each client count and workload. Image order reverses on the second pass. Each client immediately replaces its completed request. A completed cycle of clients fills the queue before timing starts; the final drain is excluded from throughput. Each worker discards a seed-9001 warmup, then checks the seed-42 golden recording across images. Every load-test response, including fill and drain, must match that golden. All measured weights remain resident.

Plain uses the existing paragraph. Processed uses two SSML turns with rate/pitch/volume, a 120 ms pause and whole-recording normalization. Each workload repeats one fixed seed (42), so audio duration and request content remain identical across clients, passes and images. This isolates scheduling; it is not a diverse production-traffic simulation.

Sampling: temperature 0.9, top-k 50, repetition penalty 1.05, token cap 600, codec chunk size 8, complete WAV responses. GPU sampling requested every 0.25 seconds; queue sampling every 0.05 seconds. Client occupancy is integrated from actual send/receive transitions. Queue depth is time-weighted from timestamped status samples. Latencies describe requests completing inside the steady window, including their queue wait. Complete-response latency is not a streaming first-audio measurement.

| Workload | Clients | Before req/s | After req/s | Throughput change | Pass change range | Completed before / after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| plain | 4 | 0.2500 | 0.2500 | +0.00% | +0.00% to +0.00% | 45 / 45 |
| plain | 8 | 0.2444 | 0.2444 | +0.00% | -4.35% to +4.76% | 44 / 44 |
| processed | 4 | 0.4000 | 0.4500 | +12.50% | +5.26% to +20.59% | 72 / 81 |
| processed | 8 | 0.3944 | 0.4667 | +18.31% | +16.67% to +20.00% | 71 / 84 |

Completed-request counts have finite-window boundary variation. Pass results below show repeatability; two passes do not establish statistical confidence or a universal speedup. Keep the burst benchmark as a separate workload.

| Pass | Image | Workload | Clients | Req/s | Mean outstanding | Mean waiting | Median latency s | p95 latency s | Mean GPU use % | Peak VRAM MiB | Valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | before | plain | 4 | 0.2444 | 4.000 | 3.010 | 16.485 | 16.912 | 86.7 | 6215 | True |
| 1 | before | plain | 8 | 0.2333 | 8.000 | 7.011 | 33.017 | 34.394 | 83.7 | 6321 | True |
| 1 | before | processed | 4 | 0.3778 | 4.000 | 3.013 | 10.026 | 11.939 | 64.6 | 6006 | True |
| 1 | before | processed | 8 | 0.4000 | 8.000 | 7.012 | 20.075 | 21.493 | 68.2 | 6643 | True |
| 1 | after | plain | 4 | 0.2444 | 4.000 | 3.009 | 16.074 | 16.466 | 80.7 | 6340 | True |
| 1 | after | plain | 8 | 0.2444 | 8.000 | 7.008 | 32.664 | 33.374 | 83.9 | 6226 | True |
| 1 | after | processed | 4 | 0.4556 | 4.000 | 2.920 | 8.764 | 9.129 | 74.2 | 6632 | True |
| 1 | after | processed | 8 | 0.4667 | 8.000 | 6.915 | 16.878 | 17.087 | 73.7 | 6673 | True |
| 2 | after | processed | 8 | 0.4667 | 8.000 | 6.921 | 16.987 | 17.242 | 71.7 | 6301 | True |
| 2 | after | processed | 4 | 0.4444 | 4.000 | 2.913 | 8.674 | 9.570 | 71.9 | 6347 | True |
| 2 | after | plain | 8 | 0.2444 | 8.000 | 7.007 | 32.301 | 33.742 | 84.1 | 6535 | True |
| 2 | after | plain | 4 | 0.2556 | 4.000 | 3.009 | 15.250 | 15.467 | 83.8 | 6835 | True |
| 2 | before | processed | 8 | 0.3889 | 8.000 | 7.012 | 19.915 | 22.461 | 63.0 | 6497 | True |
| 2 | before | processed | 4 | 0.4222 | 4.000 | 3.015 | 9.439 | 9.860 | 68.5 | 6701 | True |
| 2 | before | plain | 8 | 0.2556 | 8.000 | 7.010 | 31.077 | 31.341 | 83.7 | 6706 | True |
| 2 | before | plain | 4 | 0.2556 | 4.000 | 3.007 | 15.455 | 16.110 | 83.9 | 6721 | True |

GPU use and peak VRAM include the Windows desktop. GPU telemetry covers fill and drain as well as the steady window. The status GPU-lease counter measures ownership, not CUDA kernel activity. Older runtimes omit the total synthesis-inflight counter; client occupancy remains available for both images.

Run: `20261025-133452-01ae7831`; harness `bd3b7fd6721c6a373a868e07ec86d869ad1eb2ec20737fbcc24d24306ed42c56`; driver `74eb16206e1f2d8b657d61673df7105e13ce61c1be56badacb1d121c7ed15d9f`.

## Preserved images

- before: `sha256:63a896184e6d923c6d46951ceff7cce23e269147f798f82e796ffbea41a0ee21`
- after: `sha256:fa9feee18805baf6ce4b44cc1d0e7d7cb36cc3f519a5d9361dd2968042d57797`

Pass 1 before inference hash: `a439964836205203eca9f608ffe3b7e179d4627628f49ca806aef534b5e1259b`.

Pass 1 after inference hash: `812c76c465b996215abcc326034688765e31c704beb98a41c7616afbd822edec`.

Pass 2 after inference hash: `812c76c465b996215abcc326034688765e31c704beb98a41c7616afbd822edec`.

Pass 2 before inference hash: `a439964836205203eca9f608ffe3b7e179d4627628f49ca806aef534b5e1259b`.

No other inference service is stopped. Model cache is mounted read-only in temporary workers, and the original Studio container is restored after the run.
