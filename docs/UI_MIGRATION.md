# Demo-to-Studio review

Reviewed and updated on 2026-10-24 against the upstream demo HTML/server and
the active `src/faster_qwen3_tts/standalone_ui/` implementation. All six gaps from the
initial review are now addressed. Studio additions, including Base delivery
direction, saved voices, editing, GPU telemetry and expanded controls, are retained.
After the final parity check, the original demo was removed on 2026-10-24 with
the operator's authorization. Its original source remains in Git history.

## Completed migration fixes

| Item | Old demo | Current Studio | Status |
| --- | --- | --- | --- |
| Repeated reference preparation | Uses stable content-derived file paths to reuse prepared prompts. | Keys prepared prompts by reference content and relevant clone settings. LRU cache holds at most eight entries and 8 MiB of tensors in system RAM, cleared on model unload. Uploaded files remain temporary. | Fixed and tested across separate upload paths, changed content/settings, eviction, memory limits and unload. |
| Microphone selection | Device list with exact-device capture and refreshed permission labels. | System-default or selected device, refresh button, refreshed names after permission, disconnect handling and actionable permission errors. Controls are beside recording. | Restored; browser tests use synthetic devices. Physical-device verification remains a manual check. |
| Queue feedback | Streaming requests show requests ahead. | Generation requests enter a FIFO queue, cancelled waiters are removed, and position updates reach the browser for both complete and streaming output. Model loading is a separate progress state. | Restored and extended; cancellation/ordering tests and real browser queue check pass. |
| Diagnostic timings | Model TTFA, client latency, preparation estimate, buffered audio, duration and speed. | Diagnostics show queue/load/reference preparation, cache reuse, server first audio, reported streaming model timings, browser first-chunk/scheduled playback and live buffer. Missing measurements are labelled unavailable. | Restored with explicit timing definitions; old/new timings are not equivalent benchmarks. |
| Chunk-size selection | Integer slider from 1 to 24 codec frames. | Slider and exact number from 1 to 64, with approximate audio duration and client/server validation. | Restored and expanded. |
| Clone defaults | UI uses transcript-assisted cloning and incremental Base text input; other variants use whole text. | UI/API defaults follow those workflows. Explicit text-input choices survive switching workflows and model sizes within the page. | Aligned; reset affects the current workflow, preserving choices elsewhere. |

The original reference-reuse regression was reproduced through the actual request
path before repair. The regression test now verifies that two identical uploads
with different temporary paths perform one extraction and create one cache entry.
Real GPU inference also reports a cache hit on reuse. These are correctness checks,
not representative latency or VRAM benchmarks.

## Capabilities already available

| Demo capability | Studio equivalent |
| --- | --- |
| Five official model checkpoints and loading state | Capability-driven model choices, loading on demand, System load/unload and runtime badge |
| Description-based voice design | Voice design view, with generated samples reusable for cloning |
| Built-in CustomVoice speakers and applicable instructions | Generate view, nine speakers, instructions on 1.7B CustomVoice |
| Reference cloning, speaker-only and transcript-assisted methods | Voice clone view with both methods |
| Upload and record reference audio, preview playback | Upload/drop/record surface with waveform editor, playback and trimming |
| Reference transcription | Explicit Transcribe reference action through an operator-configured ASR service |
| Fixed reference slots with transcripts | Explicit saved-voice library; uploaded audio can be saved by the operator |
| Complete and streaming synthesis, WAV download | Shared inference API, incremental playback and downloadable WAV editor |
| Language selection | All ten model languages plus Auto |
| Temperature, top K and repetition penalty | Sliders and exact numeric fields; ranges include the old ranges |
| Whole-text and incremental text delivery | Text delivery control, independent from playback streaming |
| Ctrl/Cmd+Enter generation | Generates or stops in the active workflow |
| Wrong-model guidance and model switching | Workflow-filtered selection, request validation and automatic loading of the requested checkpoint |
| Text/upload size checks | Same 1,000-character text and 10 MB upload limits, plus bounded decoding and reference duration |

Base delivery direction is an engine capability added to the Studio. Although
the old server accepted a general `instruct` form field, neither its clone UI
request nor its clone-generation calls forwarded that field. The Studio now
forwards it in complete and streaming Base generation, with experimental-support
guidance. It should not be described as a feature already exposed by the old UI.

## Deliberate scope and interaction differences

- The Studio targets NVIDIA/Torch. GGML backend selection, GGUF quantization and
  cross-backend comparison have not been migrated into the product UI.
- Hugging Face login, accounts, quotas and the old hosted-demo access controls
  are outside the current local Studio scope.
- Local nano-parakeet transcription is replaced by an existing configurable ASR
  service. Testing does not launch a local ASR model.
- Transcription requires an explicit action rather than automatically sending a
  reference after every upload or recording. Manual transcript entry remains usable.
- The Hangry Labs shell uses its dark visual style; the demo's light/dark toggle
  and theme preference are not carried over.
- Complete generation presents an audio editor with a Play control; streaming
  plays incrementally. The old demo attempted to autoplay complete results.
- System now supplies persistent per-workflow defaults, startup preloading and
  multi-model residency, with a global switch for request-only loading. The old
  demo's model allowlist environment variable is not a Studio control.
- Old route names and form contracts are replaced by Studio routes. No legacy
  API compatibility is claimed. Endpoint documentation is available in the API view.
- Text areas are explicitly resizable rather than using the demo's automatic
  growth behavior. The new recorder shows a waveform and elapsed time rather
  than the old waiting-for-signal status and level meter.

These choices are separate from the missing controls and performance concern
above. Review any interaction difference that should become a product preference.

## Retirement

The demo source, Hugging Face Space publisher helper, legacy Task/PowerShell
action, Docker copies/environment, package extra, manifest rule and demo-only
tests are removed. Documentation now points to the Studio. A real fresh-start
test verifies the Studio starts without network access, models, accounts or
inherited recordings.

Local-ASR benchmark helpers and their unused notices have also been removed.
Studio transcription uses the configured external service. Model inference is
maintained locally; see [upstream sources](UPSTREAMS.md).

Core GPU synthesis and remote-ASR checks during migration covered all five
checkpoints and Base directions. The fixes add CPU regression tests and focused
0.6B GPU checks for cache reuse, both clone methods, exact chunk size and progress
in both output modes. This does not claim new perceptual-quality, physical-device
or performance-benchmark qualification.
