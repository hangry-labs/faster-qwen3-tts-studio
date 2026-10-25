# GPU memory details

Run `20261025-053632-9d5b8428` on NVIDIA GeForce RTX 5070 Ti.
Workload SHA-256: `6a968ddb530f978637db9ced405ab459fd3d437bdad8eb89caf9538d94958a46`. Reference SHA-256: `0a70c960986c7ddaad57a4fbd7c28209ab8911580f610f23d1363403346eb4d4`.
Fixed per-call seeds, concurrency one, explicit settings and discarded warmups. Checkpoints are never pooled.

## faster / 1.7B-CustomVoice / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.037s; cold load 14.681s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-CustomVoice`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Warm peak delta MiB | Measured calls |
|---|---|---|
| Mode: custom | 6118 | 100 |
| Language: Chinese | 5337 | 10 |
| Language: English | 5093 | 10 |
| Language: French | 5569 | 10 |
| Language: German | 5781 | 10 |
| Language: Italian | 5766 | 10 |
| Language: Japanese | 6118 | 10 |
| Language: Korean | 5617 | 10 |
| Language: Portuguese | 5617 | 10 |
| Language: Russian | 5598 | 10 |
| Language: Spanish | 5599 | 10 |

## faster / 1.7B-Base / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.047s; cold load 14.210s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-Base`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Warm peak delta MiB | Measured calls |
|---|---|---|
| Mode: clone | 6587 | 30 |
| Language: Chinese | 6027 | 3 |
| Language: English | 5753 | 3 |
| Language: French | 6059 | 3 |
| Language: German | 6062 | 3 |
| Language: Italian | 6340 | 3 |
| Language: Japanese | 6366 | 3 |
| Language: Korean | 6573 | 3 |
| Language: Portuguese | 6587 | 3 |
| Language: Russian | 6489 | 3 |
| Language: Spanish | 6479 | 3 |

## faster / 1.7B-VoiceDesign / complete

Image `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`; source `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.
API ready 2.068s; cold load 5.943s; discarded warmups 1. Incremental waveform support: True.

Resident cohort: `1.7B-VoiceDesign`.
Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.

| Group | Warm peak delta MiB | Measured calls |
|---|---|---|
| Mode: design | 5443 | 100 |
| Language: Chinese | 5417 | 10 |
| Language: English | 4959 | 10 |
| Language: French | 5138 | 10 |
| Language: German | 5230 | 10 |
| Language: Italian | 5087 | 10 |
| Language: Japanese | 5077 | 10 |
| Language: Korean | 5192 | 10 |
| Language: Portuguese | 5200 | 10 |
| Language: Russian | 5443 | 10 |
| Language: Spanish | 5432 | 10 |

