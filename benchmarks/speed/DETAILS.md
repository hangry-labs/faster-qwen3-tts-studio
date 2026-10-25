# Inference speed details

Run `20261025-053632-9d5b8428` on NVIDIA GeForce RTX 5070 Ti.
Workload SHA-256: `6a968ddb530f978637db9ced405ab459fd3d437bdad8eb89caf9538d94958a46`. Reference SHA-256: `0a70c960986c7ddaad57a4fbd7c28209ab8911580f610f23d1363403346eb4d4`.
Fixed per-call seeds, concurrency one, explicit settings and discarded warmups. Checkpoints are never pooled.

## faster / 1.7B-CustomVoice / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.037s; cold load 14.681s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-CustomVoice`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Completed | Realtime speed (×) | Median RTF | p95 RTF |
|---|---|---|---|---|
| Mode: custom | 100/100 | 2.88 | 0.348 | 0.369 |
| Language: Chinese | 10/10 | 2.96 | 0.335 | 0.362 |
| Language: English | 10/10 | 2.97 | 0.337 | 0.347 |
| Language: French | 10/10 | 2.96 | 0.340 | 0.365 |
| Language: German | 10/10 | 2.84 | 0.351 | 0.359 |
| Language: Italian | 10/10 | 2.83 | 0.355 | 0.372 |
| Language: Japanese | 10/10 | 2.76 | 0.360 | 0.384 |
| Language: Korean | 10/10 | 2.84 | 0.350 | 0.359 |
| Language: Portuguese | 10/10 | 2.85 | 0.349 | 0.370 |
| Language: Russian | 10/10 | 2.87 | 0.349 | 0.354 |
| Language: Spanish | 10/10 | 2.93 | 0.342 | 0.358 |

## faster / 1.7B-Base / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.047s; cold load 14.210s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-Base`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Completed | Realtime speed (×) | Median RTF | p95 RTF |
|---|---|---|---|---|
| Mode: clone | 30/30 | 2.94 | 0.339 | 0.357 |
| Language: Chinese | 3/3 | 2.97 | 0.335 | 0.340 |
| Language: English | 3/3 | 2.95 | 0.340 | 0.341 |
| Language: French | 3/3 | 3.05 | 0.328 | 0.330 |
| Language: German | 3/3 | 2.99 | 0.333 | 0.337 |
| Language: Italian | 3/3 | 2.94 | 0.342 | 0.344 |
| Language: Japanese | 3/3 | 2.95 | 0.337 | 0.346 |
| Language: Korean | 3/3 | 2.88 | 0.344 | 0.355 |
| Language: Portuguese | 3/3 | 3.01 | 0.333 | 0.333 |
| Language: Russian | 3/3 | 2.80 | 0.358 | 0.373 |
| Language: Spanish | 3/3 | 2.90 | 0.344 | 0.351 |

## faster / 1.7B-VoiceDesign / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.068s; cold load 5.943s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-VoiceDesign`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Completed | Realtime speed (×) | Median RTF | p95 RTF |
|---|---|---|---|---|
| Mode: design | 100/100 | 2.86 | 0.348 | 0.376 |
| Language: Chinese | 10/10 | 2.67 | 0.371 | 0.397 |
| Language: English | 10/10 | 2.76 | 0.359 | 0.380 |
| Language: French | 10/10 | 2.77 | 0.363 | 0.374 |
| Language: German | 10/10 | 2.87 | 0.346 | 0.372 |
| Language: Italian | 10/10 | 2.95 | 0.338 | 0.349 |
| Language: Japanese | 10/10 | 2.92 | 0.343 | 0.351 |
| Language: Korean | 10/10 | 2.96 | 0.343 | 0.346 |
| Language: Portuguese | 10/10 | 2.94 | 0.339 | 0.353 |
| Language: Russian | 10/10 | 2.89 | 0.346 | 0.361 |
| Language: Spanish | 10/10 | 2.80 | 0.354 | 0.373 |

