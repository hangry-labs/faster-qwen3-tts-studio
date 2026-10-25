# 0.6B product baseline, 2026-10-25

Faster Qwen only, with **one checkpoint resident at a time**. Each checkpoint stayed loaded through its applicable suites, then unloaded before the next. No standard-engine comparison ran.

Run `20261025-050404-08222176`. NVIDIA GeForce RTX 5070 Ti, 16303 MiB, driver 610.88. Other inference workloads were stopped; the Windows desktop remained active.

Runtime: Python 3.13.17, Torch 2.10.0+cu128, Transformers 5.15.1, Triton 3.6.0,
Hugging Face Hub 1.28.0 and ssml-h-tools 0.3.1. BF16, SDPA, one inference worker;
temperature 0.9, top-k 50, repetition penalty 1.05 and a 600-token output cap.

310 measured requests across ten languages, plus seven discarded warmup requests. There were 130 complete responses, 130 SSE streams, ten ten-turn SSML documents and 40 requests across five paired four-client queue rounds. Loading, reference registration and warmups are excluded from warmed request times.

## Speed and first audio

Realtime speed is total generated audio duration divided by total request time;
higher is better. 3.3x means 3.3 seconds of audio generated per second. RTF is
request time divided by audio duration; lower is faster. First audio is the
first decoded nonempty SSE chunk, including HTTP transport. It is not browser
playback or speaker output latency. All 260 ordinary generation requests are
judged remotely after every TTS measurement finishes.

| Checkpoint | Delivery | Calls | Realtime speed (×) | Median RTF | p95 RTF | Median first audio ms | p95 first audio ms | Mean ASR similarity % | Exact transcript % |
|---|---|---|---|---|---|---|---|---|---|
| 0.6B-CustomVoice | complete | 100 | 3.30 | 0.303 | 0.319 | n/a | n/a | 99.36 | 83.00 |
| 0.6B-Base | complete | 30 | 3.29 | 0.305 | 0.316 | n/a | n/a | 97.94 | 20.00 |
| 0.6B-CustomVoice | streaming | 100 | 2.79 | 0.356 | 0.396 | 303.8 | 353.6 | 99.32 | 82.00 |
| 0.6B-Base | streaming | 30 | 2.89 | 0.347 | 0.361 | 312.5 | 364.4 | 98.08 | 26.67 |

Streaming uses chunk size 8, a single plain-text unit, neutral prosody and disabled finishing/loudness normalization. Multi-turn markup and audio processing can buffer larger units. Per-call chunk arrivals, largest arrival gaps and complete request times are retained in the [streaming details](streaming/DETAILS.md).

## Memory and loading

Whole-device idle baseline was 2393 MiB before model loading. Device peaks include the desktop, driver and all CUDA allocations. Torch peaks cover the worker allocator and capture short allocation peaks that device polling may miss. These counters are not interchangeable.

The following are the highest observed values across all applicable suites for each checkpoint. Cold process loading includes graph preparation using already cached model files; it is not a cold-disk or download benchmark.

| Checkpoint | Torch peak allocated MiB | Torch peak reserved MiB | Device peak MiB | Container peak RAM MiB | Load s | Unload s |
|---|---|---|---|---|---|---|
| 0.6B-CustomVoice | 2862.1 | 3646.0 | 6341 | 2582.4 | 5.224 | 0.272 |
| 0.6B-Base | 2892.9 | 3926.0 | 6666 | 2298.3 | 5.970 | 0.220 |

Both checkpoint unloads returned Torch allocated and reserved counters to zero. All warmed measured requests reported zero model-loading time, and each profile verified that only its own checkpoint remained resident. Device sampling targeted 100 ms; actual process-launch/poll cadence is recorded in raw evidence. Container peak RAM is cumulative within each checkpoint worker.

## Dialogue and queue reliability

- ssml: 5/5 passed; 5/5 complete tails; mean transcript similarity 100.00%.
- ssml-h: 5/5 passed; 5/5 complete tails; mean transcript similarity 100.00%.
- FIFO: 20/20 paired WAVs byte-identical; peak active 1, peak waiting 3, monitor errors 0.
- Sequential batches total 77.421s; queued batches 79.195s (-2.24% throughput change). FIFO serializes access; this is not model-level parallel inference.

SSML completion requires at least 95% transcript similarity, all ten ordered turn endings and the final tail. 0.6B CustomVoice does not support delivery instructions: this run tests Ryan/Aiden dialogue in both input modes without directions. Directed SSML-H and experimental Base direction following are not measured here.

## Reproduction and limits

Run `task benchmark-build`, `task benchmark-preflight`, then `task benchmark-full` with the existing remote ASR service configured. Reuse the same authorized reference WAV and exact transcript for before/after comparisons. No local ASR model runs.

Reference WAV SHA-256: `0a70c960986c7ddaad57a4fbd7c28209ab8911580f610f23d1363403346eb4d4`. The recording is a synthetic VoiceDesign sample reused from preliminary smoke, excluded from this run's timings and not distributed in the repository.

Workload SHA-256: `fe33ca6c315adffed586ff15ecf4a480cd4b6583ba0ce7f4a22141da46804cf1`.
Harness SHA-256: `c9fc4ec8e3dc7d7da1ed4ae54bfd018a9fdc488fdeaaf97a3fa6deb4162ecdde`.

Local benchmark image identity: `sha256:10db59f376a1ae730f0eb7f9ff0d5910c6faf23f5510a94514e34ba6f477d03c`.
Installed inference source SHA-256: `36fa150a0cff236e299313ba0bbb80eff74ba2c7af7dfd90b2a706901056c29b`.

Pinned checkpoint revisions:

- `0.6B-CustomVoice`: `85e237c12c027371202489a0ec509ded67b5e4b5`.
- `0.6B-Base`: `5d83992436eae1d760afd27aff78a71d676296fc`.

Remote judge: `Qwen/Qwen3-ASR-0.6B-hf`. ASR similarity measures transcript fidelity, not naturalness, expressiveness, speaker identity or direction following. Exact transcript rates can be affected by recognition errors and orthography. This is one workstation session with repeated fixed-seed calls, not a confidence interval or release qualification. VoiceDesign has no 0.6B checkpoint and is reserved for a separate 1.7B run.

Base's 20% complete-response exact-transcript rate deserves attention alongside
its 97.94% mean similarity. Several reviewed discrepancies concern the inherited
corpus names “VoxCPMTTS” and “Hangry Labs,” including phonetic spellings and
recognition variants. There are other word differences too; this run does not
separate synthesis mistakes from ASR mistakes. The unmodified 0.6B transcripts
and lowest-scoring cases remain in local raw history and audio evidence.
Rolling detail files describe the latest recorded run, which can use a
different model size; the history tables retain both sizes.

Detailed reports: [speed](speed/BENCHMARKS.md), [memory](memory/gpu/BENCHMARKS.md), [transcript fidelity](speech-quality/BENCHMARKS.md), [streaming](streaming/BENCHMARKS.md), [SSML](ssml/BENCHMARKS.md), [queue](inference_queue/BENCHMARKS.md). Raw JSON, WAVs, partial journals and worker logs remain in ignored local artifacts.
