# Release notes

## v1.0-snapshot

- Record the 1.7B baseline: 510 measured requests across CustomVoice, Base and
  VoiceDesign, one model loaded at a time. Complete-response realtime speeds
  were 2.88x, 2.94x and 2.86x respectively on the test workstation. Retain
  transcript outliers alongside the latency, memory, directed SSML-H and FIFO
  results; the 0.6B history remains available.
- Label benchmark throughput as Realtime speed and lead speed tables with that
  multiplier. Define 3.3x as 3.3 seconds of generated audio per second; retain
  RTF and streaming latency as separate measurements.
- Record the first isolated 0.6B product baseline: 310 measured Faster Qwen
  requests across ten languages, complete and streaming speech, ten complete
  SSML dialogues and 20 identical FIFO output pairs. Preserve per-model memory,
  startup/teardown and transcript-fidelity results in the benchmark reports.
- Add `task benchmark-full` for a Faster Qwen product baseline: complete speech,
  streaming, SSML and FIFO tests with one checkpoint resident at a time. Keep
  model load/unload timings separate, verify zero loading in warmed calls,
  record Torch peak memory and streaming chunk arrivals, and judge recordings
  remotely after every TTS measurement has finished. Standard-engine comparisons
  are optional diagnostics and are excluded from the product run.
- Add persisted per-workflow model defaults and GPU residency controls in System.
  Keep 0.6B Base and CustomVoice plus 1.7B VoiceDesign ready by default. Request-only
  weights release after the complete request; pinned models can coexist. Expose
  per-model loading failures without silently evicting other pinned weights.
- Release captured CUDA graphs and cached BLAS workspaces on full unload,
  returning GPU allocator memory instead of leaving reserved multi-gigabyte pools.
- Default baseline and streaming benchmarks to warmed, resident 0.6B checkpoints;
  keep explicit 1.7B design and directed-SSML coverage separate.
- Complete the first shared-GPU smoke: all five suites and 40 measured requests
  passed, including ten-turn SSML completion and four-client FIFO WAV identity.
  Retain the results as preliminary evidence, separate from official history.

- Add the manual VoxCPMTTS-style benchmark suite: isolated native/faster workers,
  five pinned checkpoints, multilingual speed/memory/ASR fidelity reports,
  streaming first-audio measurements, queue identity checks and paired ten-turn
  SSML reliability. Planning and offline tests are available before any real
  GPU baseline is collected.

The first Hangry Labs Studio development version. Python distributions use the
PEP 440 version `1.0.dev0`. This snapshot name does not create a stable release
or change the rolling Docker image tags.

- Maintain Qwen inference, compatibility changes and accelerated generation
  locally under `src/`, with provenance for all three upstream sources.
- Package the Studio for NVIDIA GPUs with Python 3.13 and local model caches.
- Provide voice design, saved-voice cloning with experimental delivery direction,
  built-in speakers, OpenAI-compatible speech and native speech APIs.
- Support Text, standard SSML, SSML-H and the Magic dialogue editor, including
  per-turn takes, retained takes, designed characters and saved workspaces.
- Isolate Text and SSML drafts when switching input modes. Import edited SSML-H
  into Magic only after validation, preserving the active draft on errors.
- Align Generate with the compact VoxCPMTTS layout, generation menus, joined
  Generate/Stream control, progress display, waveform players and finishing UI.
- Assemble completed Magic takes automatically after turn edits. Save settings,
  original output and processed previews with dialogue workspaces.
- Track progress per request. Preview MP3 streams progressively and retain the
  same recording for replay, download and finishing. Stream mode uses MP3;
  Generate mode uses the selected output format.
- Add bounded FFmpeg noise cleanup, EQ, compression, loudness normalization and
  optional pitch/speed shaping, with separate original and processed previews.
- Protect audio replacement from stale loads clearing newer recordings.

Native speaker direction requires the 1.7B CustomVoice model. Base delivery
direction remains experimental. Finishing uses FFmpeg; Signalsmith processing
and VoxCPM-specific model controls are not offered by this engine. Word timing
and subtitle export are not available. See [API capabilities](API.md) for the
supported input semantics and limits.
