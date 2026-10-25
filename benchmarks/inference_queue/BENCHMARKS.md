# Inference queue throughput

One GPU worker; alternate batch order each round. Queued latency includes waiting time. A throughput change is not a claim that FIFO accelerates model inference.

| Run | Engine | Checkpoint | Clients | Rounds | Sequential s | Queued s | Throughput change % | Identical WAVs | Peak queue | Pass |
|---|---|---|---|---|---|---|---|---|---|---|
| 20261025-050404-08222176 | faster | 0.6B-CustomVoice | 4 | 5 | 77.421 | 79.195 | -2.24 | 20/20 | 3 | True |
| 20261025-053632-9d5b8428 | faster | 1.7B-CustomVoice | 4 | 5 | 88.723 | 88.070 | 0.74 | 20/20 | 3 | True |

