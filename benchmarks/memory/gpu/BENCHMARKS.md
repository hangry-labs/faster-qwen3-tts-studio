# GPU memory

Whole-device MiB minus the pre-load baseline. Resident-cohort rows include every listed checkpoint, not just the measured model. Torch peaks and cgroup RAM cover that worker and its entire cohort; loading is separate from warmed calls.

| Run | Engine | Checkpoint | Delivery | Resident cohort | VRAM baseline MiB | Warm peak delta MiB | Load peak delta MiB | Torch peak allocated MiB | Torch peak reserved MiB | RAM current MiB | RAM peak MiB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20261025-050404-08222176 | faster | 0.6B-CustomVoice | complete | 0.6B-CustomVoice | 2393 | 3316 | 2729 | 2617.24 | 2970.0 | 2060.0 | 2211.7 |
| 20261025-050404-08222176 | faster | 0.6B-Base | complete | 0.6B-Base | 2393 | 4230 | 2700 | 2892.87 | 3924.0 | 2169.2 | 2216.6 |
| 20261025-053632-9d5b8428 | faster | 1.7B-CustomVoice | complete | 1.7B-CustomVoice | 2393 | 6118 | 4609 | 4669.22 | 5286.0 | 2150.1 | 2247.3 |
| 20261025-053632-9d5b8428 | faster | 1.7B-Base | complete | 1.7B-Base | 2393 | 6587 | 4671 | 4847.45 | 6002.0 | 5624.6 | 5669.6 |
| 20261025-053632-9d5b8428 | faster | 1.7B-VoiceDesign | complete | 1.7B-VoiceDesign | 2393 | 5443 | 4726 | 4532.32 | 4850.0 | 2093.0 | 2237.9 |

See [DETAILS.md](DETAILS.md) for the latest run and methodology.

