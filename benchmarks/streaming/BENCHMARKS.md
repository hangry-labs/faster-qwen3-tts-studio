# Streaming latency

Client TTFA starts before the HTTP request and ends at the first decoded nonempty SSE audio chunk. Standard Qwen emits one buffered recording; this is not incremental synthesis. SSE transport excludes browser playback buffering.

| Run | Engine | Checkpoint | Incremental | Calls | Realtime speed (×) | Median TTFA ms | p95 TTFA ms | Median RTF | p95 RTF | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| 20261025-050404-08222176 | faster | 0.6B-CustomVoice | True | 100 | 2.79 | 303.8 | 353.6 | 0.356 | 0.396 | 0 |
| 20261025-050404-08222176 | faster | 0.6B-Base | True | 30 | 2.89 | 312.5 | 364.4 | 0.347 | 0.361 | 0 |
| 20261025-053632-9d5b8428 | faster | 1.7B-CustomVoice | True | 100 | 2.51 | 327.2 | 375.1 | 0.397 | 0.430 | 0 |
| 20261025-053632-9d5b8428 | faster | 1.7B-Base | True | 30 | 2.61 | 341.7 | 386.8 | 0.382 | 0.407 | 0 |
| 20261025-053632-9d5b8428 | faster | 1.7B-VoiceDesign | True | 100 | 2.46 | 328.3 | 372.8 | 0.406 | 0.438 | 0 |

