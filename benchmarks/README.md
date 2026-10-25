# Hangry Labs Qwen benchmark suite

Manual, Docker-first benchmarks adapted from
[VoxCPMTTS](https://github.com/hangry-labs/VoxCPMTTS). They measure speed, GPU
memory and transcript fidelity separately. The [first 0.6B baseline](BASELINE_RESULTS.md)
completed 310 measured requests with one checkpoint loaded at a time.
The [1.7B baseline](BASELINE_1.7B_RESULTS.md) adds 510 requests across CustomVoice,
Base and VoiceDesign, including directed SSML-H completion checks.
The initial [shared-GPU smoke](SMOKE_RESULTS.md)
covered the original five suites. The product baseline uses Faster Qwen only;
standard-engine comparisons are optional historical diagnostics. Planning,
synthetic HTTP tests and CPU adapter tests do not establish GPU performance.

```powershell
task benchmark-build
task benchmark-preflight
task benchmark-plan
```

These commands build the harness, inspect cached checkpoints and show the
workload. They do not load a model or run GPU inference. Prepare the product
image and its pinned model cache first. `task init` builds the product image;
normal Studio use or a full image populates its model cache. Benchmarks run
offline against those cached weights. Optional `task benchmark-preflight --
--hash-files` computes SHA-256 for every cached file, including weights.

When the selected GPU is available exclusively for benchmarking:

```powershell
# First real check: one English CustomVoice request per engine, plus warmups.
task benchmark-baseline-smoke -- --models 0.6B-CustomVoice

# Product smoke suites, including the four-client FIFO check.
task benchmark-smoke

# Full product baseline, one checkpoint loaded at a time.
task benchmark-full

# Full multilingual baseline and its separate speed/memory/quality reports.
task benchmark-baseline -- --comment "initial v1.0-snapshot baseline"

# Additional suites, using the same isolated worker lifecycle.
task benchmark-backends
task benchmark-streaming
task benchmark-ssml
task benchmark-queue
```

Set `QWEN_STUDIO_ASR_URL`, use Task's `ASR_URL` variable, or pass `--asr-url` to
the existing remote Qwen3-ASR service. No local ASR model is started. The queue
suite does not need ASR. The baseline and streaming suites intersect the ten
Qwen-supported languages in [corpus.json](corpus.json) with the judge's advertised
language support; explicit unknown language filters fail.

## Suites and evidence

| Area | Task | Reports |
| --- | --- | --- |
| Warmed inference speed | `benchmark-baseline` | [speed](speed/BENCHMARKS.md) |
| GPU memory and container RAM | `benchmark-baseline` | [memory/gpu](memory/gpu/BENCHMARKS.md) |
| Transcript fidelity and repeat consistency | `benchmark-baseline` | [speech-quality](speech-quality/BENCHMARKS.md) |
| Four-scenario engine pilot | `benchmark-backends` | [backend_comparison](backend_comparison/BENCHMARKS.md) |
| First audio and complete stream latency | `benchmark-streaming` | [streaming](streaming/BENCHMARKS.md) |
| Paired ten-turn standard SSML and SSML-H | `benchmark-ssml` | [ssml](ssml/BENCHMARKS.md) |
| Sequential versus FIFO-queued requests | `benchmark-queue` | [inference_queue](inference_queue/BENCHMARKS.md) |

Each suite has a `-smoke` task that retains local evidence but does not append
official history or update reports. Smoke tasks still perform real inference.
For preliminary checks while other workloads share the GPU, add
`--allow-shared-gpu`. This requires `--no-write` and records the shared-GPU
qualification in raw evidence; it cannot publish official results.
Add `--plan` for a fully offline, model-free plan instead. `task benchmark-test`
runs synthetic transport, planning, statistics, reporting and isolation tests.
CPU runtime adapter tests also run in the Docker checks target.

The baseline defaults to the `faster` engine and the two 0.6B checkpoints,
two short prompts repeated five times per language for CustomVoice/VoiceDesign,
and one clone paragraph repeated three times per language for each Base model.
That is **130 measured calls**, excluding warmups and synthetic
reference preparation. Streaming is a separate suite with the same workload.
SSML uses five fixed seeds per input mode; queue uses four clients over five
paired rounds. Model size, workflow, language and delivery mode remain separate
in raw records and report details. Use `--models all` for all five checkpoints
(360 calls per engine). The four-scenario pilot explicitly includes 1.7B VoiceDesign,
the only design checkpoint; directed SSML uses 1.7B CustomVoice. Each worker
preloads its selected model and keeps it resident throughout measurement.
Production residency settings do not preload unrelated models in individual-suite workers.

### Full product baseline

`task benchmark-full` runs the complete multilingual baseline, streaming,
ten-turn SSML/SSML-H and FIFO queue suites using Faster Qwen. It loads one
checkpoint at a time and keeps it resident through its applicable suites, then
unloads it before loading the next. This gives each model its own VRAM baseline.
The defaults are 0.6B CustomVoice and Base. VoiceDesign is a separate 1.7B run;
Qwen has no 0.6B VoiceDesign checkpoint.

There are **310 measured requests**: 130 complete, 130 streaming, ten SSML
documents and 40 requests across five paired four-client FIFO rounds. Warmups,
reference preparation, cohort loading and final unloading are separate.
0.6B CustomVoice cannot follow delivery instructions, so both markup inputs
exercise the supported ten-turn native-voice dialogue without directions.
Directed SSML-H coverage is reserved for a capable checkpoint run.

The harness verifies that only the measured checkpoint is resident before and
after each profile and rejects weight-loading telemetry in warmed calls. In addition to
sampled whole-device VRAM, it records Torch's peak allocated/reserved counters.
Streaming records median/p95 first decoded audio latency, complete request
time, chunk count and arrival gaps. These are transport measurements, not
microphone measurements of first audible sound from a browser.

Use `task benchmark-full -- --plan` to inspect the workload without inference.
Use `task benchmark-full -- --models 1.7B-CustomVoice,1.7B-Base,1.7B-VoiceDesign`
for the complete 1.7B run: 510 measured requests with one model loaded at a time.
Use `--models 1.7B-VoiceDesign` for a separate design baseline; SSML and queue
tests require CustomVoice and are omitted for design-only runs. A clone reference
is supplied with its exact transcript or generated once outside measurements.
The normal Studio is restored
after the benchmark worker exits, with its persisted residency settings intact.

Useful overrides:

```powershell
task benchmark-baseline -- --backends faster --models 1.7B-VoiceDesign --languages English,Japanese
task benchmark-baseline -- --reference-audio benchmark-data/reference.wav --reference-text "Exact permitted reference words."
task benchmark-streaming-smoke -- --models 0.6B-CustomVoice --backends faster
task benchmark-ssml-smoke -- --backends faster
task benchmark-queue-smoke -- --backends faster
```

## Measurement contract

- One worker and engine at a time, with one checkpoint resident. The full product
  run retains that checkpoint through its applicable suites. Workers bind only to loopback
  port 8812 by default, use temporary Studio/compiler data, and mount the
  existing model cache read-only. Unique ownership labels limit cleanup to
  containers created by that run. Task stops and restores only this project's
  Studio; it does not stop other GPU workloads. Arrange GPU availability first.
- Model revisions come from the product catalog. The standard adapter calls
  this repository's local `Qwen3TTSModel`; the faster worker uses the production
  `StudioEngine`. Both share the actual planner, FIFO gate, seed handling and
  encoders. The adapter exists only in the benchmark image.
- Record immutable image identity, installed source hash, dependency versions,
  checkpoint revisions, corpus hash, explicit sampling settings and reference
  hash. Before/after comparisons must preserve hardware, assets, settings,
  selected calls, reference and warmup policy. Different seeds or workloads
  cannot receive a paired engine speedup value.
- Record API startup, cold model load and discarded warmups separately from
  warmed requests. RTF is client request wall time divided by audio duration;
  lower is better. Realtime speed is total audio duration / total request time;
  higher is better. For example, 3.3x generates 3.3 seconds of audio per second.
  It is aggregated over calls, rather than the reciprocal of median RTF. Never label
  time to a complete recording as incremental TTFA.
- Streaming uses native SSE PCM WAV chunks to measure the first decoded audio
  chunk for a single plain-text speech unit, neutral prosody and no finishing
  effects or loudness normalization. Markup and processing can buffer larger
  units. It does not measure browser autoplay, MP3 encoding or playback buffers.
  Standard Qwen has no incremental waveform API here, so it emits one buffered
  recording and is labelled accordingly.
- Sample whole-device VRAM around loading and every measured request, relative
  to the pre-load baseline. The default polling target is 100ms; command latency
  limits actual cadence and very short peaks can be missed. Container RAM uses
  cgroup counters. Other GPU activity invalidates an isolated comparison.
- Stage all measured audio before remote ASR judging. Normalize transcripts
  with Unicode NFKC, case folding and removal of non-letter/non-number
  characters, as in Vox. Similarity uses sequence ratio; exact means normalized
  equality. Failed inference and failed judging remain visible in counts.
- Fixed seeds are derived from call ids. Standard and faster sampling paths
  need not produce byte-identical audio. Within-engine image comparisons can
  inspect WAV hashes, while the queue suite requires identical fixed-seed
  recordings across sequential and concurrent submission.

Cloning uses one authorized supplied reference and exact transcript, or a
synthetic VoiceDesign recording generated once before measurement. All workers
receive the same recording, registered before timed cloning calls. Warm prompt
caching is available in both engines. The standard adapter caches at most eight
prompts / 8 MiB on CPU. For before/after image runs, reuse the first run's
`reference.wav` with its recorded transcript rather than regenerating a potentially
different reference. Generated references do not establish speaker-similarity
quality, and no human recording is distributed with this suite.

## Local history and reviewed reports

Canonical raw history is kept under the git-ignored
`benchmark-artifacts/<suite>-results/runs.json`. Per-run JSON, WAV evidence,
partial-call journals and container logs live under `benchmark-artifacts/<run-id>`.
Regular benchmark tasks automatically append completed runs and regenerate
their `BENCHMARKS.md` and `DETAILS.md` reports. Tables retain earlier runs;
detail files describe the latest run. The reviewed baseline summaries are
curated separately from these generated reports.
`--results`, `--artifacts` and `--reports` override their destinations.
`--no-write` suppresses canonical history and Markdown updates while retaining
local evidence. Reports for different suites never overwrite each other.

Review generated Markdown before committing it. ASR is a comparative judge,
not ground truth or a measure of expressiveness, naturalness, prosody, direction
following or voice identity. Listen to difficult samples as well as consulting
the tables. Hardware-free tests and smoke runs are not published benchmarks.

The transcript corpus and ten-turn dialogue derive from VoxCPMTTS revision
`dde4562796ca0084a2f3df03056c6cad59686212`, under Apache-2.0. Text is retained,
including product names in the clone paragraphs, for corpus comparability;
no Vox-generated recordings or private infrastructure settings are copied.
The older upstream engine investigations remain in [research](research/README.md),
separate from this product suite and [historical upstream results](../docs/UPSTREAM_BENCHMARKS.md).
