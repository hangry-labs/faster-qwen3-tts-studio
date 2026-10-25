# Inference speed

Realtime speed is total generated audio duration / total request time; higher is better. 3.3x means 3.3 seconds of audio generated per second. RTF is request time / audio duration; lower is better. TTFA is measured only for audio events.

| Run | Engine | Checkpoint | Delivery | Completed | Realtime speed (×) | Median RTF | p95 RTF | Median client TTFA ms | TTS errors |
|---|---|---|---|---|---|---|---|---|---|
| 20261025-050404-08222176 | faster | 0.6B-CustomVoice | complete | 100/100 | 3.30 | 0.303 | 0.319 | n/a | 0 |
| 20261025-050404-08222176 | faster | 0.6B-Base | complete | 30/30 | 3.29 | 0.305 | 0.316 | n/a | 0 |
| 20261025-053632-9d5b8428 | faster | 1.7B-CustomVoice | complete | 100/100 | 2.88 | 0.348 | 0.369 | n/a | 0 |
| 20261025-053632-9d5b8428 | faster | 1.7B-Base | complete | 30/30 | 2.94 | 0.339 | 0.357 | n/a | 0 |
| 20261025-053632-9d5b8428 | faster | 1.7B-VoiceDesign | complete | 100/100 | 2.86 | 0.348 | 0.376 | n/a | 0 |

See [DETAILS.md](DETAILS.md) for the latest run and methodology.

