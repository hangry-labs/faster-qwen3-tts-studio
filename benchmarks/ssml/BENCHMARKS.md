# SSML dialogue reliability

Ten-turn dialogues with final-tail checks and fixed Ryan/Aiden voices. Delivery directions are used only on capable checkpoints; each profile records this scope. ASR is a comparative judge.

| Run | Engine | Checkpoint | Input | Passed | Rounds | Complete tails | Mean similarity % | Median RTF |
|---|---|---|---|---|---|---|---|---|
| 20261025-050404-08222176 | faster | 0.6B-CustomVoice | ssml | 5 | 5 | 5 | 100.00 | 0.335 |
| 20261025-050404-08222176 | faster | 0.6B-CustomVoice | ssml-h | 5 | 5 | 5 | 100.00 | 0.339 |
| 20261025-053632-9d5b8428 | faster | 1.7B-CustomVoice | ssml | 5 | 5 | 5 | 99.89 | 0.343 |
| 20261025-053632-9d5b8428 | faster | 1.7B-CustomVoice | ssml-h | 5 | 5 | 5 | 100.00 | 0.342 |

