# 1.7B product baseline, 2026-10-25

Faster Qwen only, with one checkpoint resident at a time: CustomVoice, Base and VoiceDesign. Each stays loaded through its applicable suites, then unloads before the next checkpoint. No standard-engine comparison ran.

Run `20261025-053632-9d5b8428` on NVIDIA GeForce RTX 5070 Ti, 16303 MiB, NVIDIA driver 610.88. Other inference workloads were stopped; the Windows desktop remained active.

Runtime: Python 3.13.17, Torch 2.10.0+cu128, Transformers 5.15.1, Triton 3.6.0, Hugging Face Hub 1.28.0 and ssml-h-tools 0.3.1.

BF16, SDPA, one inference worker; temperature 0.9, top-k 50, repetition penalty 1.05, a 600-token output cap and stream chunk size 8. Every measured request is warm, with zero weight-loading time.

510 measured requests across ten languages, plus nine discarded warmup requests: 230 complete responses, 230 SSE streams, ten ten-turn SSML documents and 40 requests across five paired four-client queue rounds. The existing remote ASR judges all 470 baseline/streaming/dialogue recordings after every TTS measurement finishes. No local ASR runs.

## Realtime speed and first audio

Realtime speed is total generated audio duration divided by total request time; higher is better. 3.0x means three seconds of generated audio per second. RTF is request time divided by audio duration; lower is better. The aggregate speed is not the reciprocal of median RTF.

| Checkpoint | Delivery | Calls | Realtime speed (×) | Median RTF | p95 RTF | Median first audio ms | p95 first audio ms | Mean ASR similarity % | Exact transcript % |
|---|---|---|---|---|---|---|---|---|---|
| 1.7B-CustomVoice | complete | 100 | 2.88 | 0.348 | 0.369 | n/a | n/a | 99.00 | 81.00 |
| 1.7B-Base | complete | 30 | 2.94 | 0.339 | 0.357 | n/a | n/a | 96.75 | 6.67 |
| 1.7B-VoiceDesign | complete | 100 | 2.86 | 0.348 | 0.376 | n/a | n/a | 99.58 | 90.00 |
| 1.7B-CustomVoice | streaming | 100 | 2.51 | 0.397 | 0.430 | 327.2 | 375.1 | 99.04 | 81.00 |
| 1.7B-Base | streaming | 30 | 2.61 | 0.382 | 0.407 | 341.7 | 386.8 | 96.74 | 6.67 |
| 1.7B-VoiceDesign | streaming | 100 | 2.46 | 0.406 | 0.438 | 328.3 | 372.8 | 99.50 | 89.00 |

First audio means the first decoded nonempty SSE waveform chunk, including HTTP transport. It excludes browser playback and speaker output latency. These streams use a single plain-text unit, neutral prosody and disabled finishing/loudness normalization. Markup and audio processing can buffer larger units.

## Memory and loading

Whole-device idle baseline was 2393 MiB. Whole-device peaks include the active desktop, CUDA driver and all allocations. Torch counters cover the worker allocator; they are not interchangeable with device totals. The table uses the highest observed value across each model's applicable suites.

Cold process loading includes graph preparation from already cached model files, not downloads or a cold-disk test. Container peak RAM is cumulative within each checkpoint worker. Loading, registration and warmups are excluded from warmed request time.

Load times are single observations. OS file-cache state was not controlled
between checkpoints, so the load-time differences are not a controlled storage
or startup comparison.

| Checkpoint | Torch peak allocated MiB | Torch peak reserved MiB | Device peak MiB | Container peak RAM MiB | Load s | Unload s |
|---|---|---|---|---|---|---|
| 1.7B-CustomVoice | 4823.6 | 5602.0 | 8511 | 2664.6 | 14.681 | 0.242 |
| 1.7B-Base | 4847.4 | 6002.0 | 9310 | 5725.4 | 14.210 | 0.315 |
| 1.7B-VoiceDesign | 4532.3 | 4854.0 | 8032 | 2484.7 | 5.943 | 0.287 |

All three unloads returned Torch allocation and reservation to zero. Each profile verified that only its own checkpoint remained resident. Device sampling targets 100 ms, with actual cadence retained in raw evidence; Torch peak counters also capture short allocation peaks.

## Dialogue and queue reliability

- ssml: 5/5 passed; 5/5 complete tails; mean transcript similarity 99.89%.
- ssml-h: 5/5 passed; 5/5 complete tails; mean transcript similarity 100.00%.
- FIFO: 20/20 paired WAVs byte-identical; peak active 1, peak waiting 3, monitor errors 0.
- Sequential batches total 88.723s; queued batches 88.070s (+0.74% throughput change). This measures serialized access, not simultaneous GPU inference.

SSML completion requires at least 95% transcript similarity, all ten ordered turn endings and the final tail. The 1.7B CustomVoice SSML-H documents also supply delivery instructions for all ten turns. Completion and ASR do not measure whether the requested emotion or delivery was convincingly followed. Experimental Base direction following is outside this baseline.

## Transcript outliers

Mean similarity should be read alongside the individual cases. Base's
complete-response exact-transcript rate was 6.67%, despite 96.75% mean
similarity. Names and acronym spellings account for some differences, but
there are also changes beyond those names.

Two complete-response samples warrant listening review:

| Checkpoint | Case | ASR similarity | Observation |
|---|---|---|---|
| CustomVoice | German, first prompt, repeat 4 | 72.94% | The expected “Der Morgenkaffee verhandelte hart, half dann aber doch.” was transcribed as “Im Morgencafé verhandelte Hart auf Dunabador.” |
| Base | French clone, repeat 1 | 83.92% | The transcript contains several altered words beyond the product and lab names. |

These are observations from the ASR judge, not confirmed synthesis errors.
The recordings and transcripts are preserved; this run does not distinguish
pronunciation problems from recognition problems. VoiceDesign's complete
samples averaged 99.58% similarity, with 90% exact matches.

## Relation to the 0.6B baseline

The [0.6B baseline](BASELINE_RESULTS.md) uses the same corpus, language counts, reference recording, sampling settings and single-model residency policy. Seeds are derived from checkpoint-specific call IDs, so model sizes use different seed values. Their descriptive results are not matched-seed pairs or a controlled per-utterance speedup. VoiceDesign has no 0.6B counterpart. This is one workstation session per size, not a confidence interval or release qualification.

## Reproduction and evidence

After preparing the product image and cached weights:

```powershell
task benchmark-build
task benchmark-preflight
task benchmark-full -- --models 1.7B-CustomVoice,1.7B-Base,1.7B-VoiceDesign
```

Configure the existing remote ASR service and reuse the recorded reference WAV with its exact transcript for repeat comparisons. Regular tasks append raw history and regenerate the per-suite Markdown reports automatically. This reviewed summary remains separate.

Reference WAV SHA-256: `0a70c960986c7ddaad57a4fbd7c28209ab8911580f610f23d1363403346eb4d4`. This synthetic VoiceDesign recording was reused from the 0.6B run, excluded from measurement and not distributed in the repository.

Workload SHA-256: `6a968ddb530f978637db9ced405ab459fd3d437bdad8eb89caf9538d94958a46`.
Harness SHA-256: `102e09183886eede1a80d744f4f1aaec65826f5c067380c9bf1075823dd48936`.
Local benchmark image identity: `sha256:908f3bcb2be48436d1bdaf273085f759d170b62f98102e44a8b7a8bc51b05631`.
Installed inference source SHA-256: `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.

Pinned checkpoint revisions:

- `1.7B-CustomVoice`: `0c0e3051f131929182e2c023b9537f8b1c68adfe`.
- `1.7B-Base`: `fd4b254389122332181a7c3db7f27e918eec64e3`.
- `1.7B-VoiceDesign`: `5ecdb67327fd37bb2e042aab12ff7391903235d3`.

Remote judge: `Qwen/Qwen3-ASR-0.6B-hf`. Transcript fidelity is not naturalness, expressiveness or speaker identity. Names, acronym spellings and recognition errors affect exact matches; the raw transcripts and audio remain available for reviewing differences. These measurements do not separate synthesis mistakes from judge mistakes.

Detailed reports: [speed](speed/BENCHMARKS.md), [memory](memory/gpu/BENCHMARKS.md), [transcript fidelity](speech-quality/BENCHMARKS.md), [streaming](streaming/BENCHMARKS.md), [SSML](ssml/BENCHMARKS.md), [queue](inference_queue/BENCHMARKS.md). Raw JSON, WAVs, worker logs and the hash-verified measured harness remain in ignored local artifacts.
