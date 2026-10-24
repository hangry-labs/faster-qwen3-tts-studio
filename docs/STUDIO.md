# Qwen3-TTS Studio

The Hangry Labs Studio is the default browser UI in the root Docker image.
It adapts the VoxCPMTTS shell, audio editor, recording controls, and GPU monitor
to Qwen's generation capabilities. It replaces the upstream demo.

```powershell
task init
task start
# Open http://127.0.0.1:7860
```

Generate loads the selected model when needed; the runtime badge shows its state.
Tiny downloads uncached models. Full seeds its baked files into an empty product
cache before starting the UI and defaults to offline operation. See the
[container workflow](RELEASING.md) for build targets and publishing rules.
The five model revisions are fixed to
the versions reviewed in the licensing audit. One TTS model occupies the GPU at
a time; switching releases the previous model first.

## Workflows

| View | Model | Workflow |
| --- | --- | --- |
| Generate | CustomVoice, Base and document-defined VoiceDesign | Magic dialogue, text, SSML and SSML-H; native or saved voices; locked takes and saved scripts. |
| Voice design | 1.7B VoiceDesign | Describe a voice, generate a sample, then use or save it as a cloning reference. |
| Voice clone | 0.6B or 1.7B Base | Upload, record, or choose a saved reference. Clone speaker identity alone or use an exact reference transcript, with optional delivery direction. |
| API | Same inference engine | Inspect capabilities and endpoint documentation. |
| System | Operator controls | Load/unload models, configure ASR, and inspect demand-driven GPU telemetry. |

All voice workflows offer complete WAV output and incremental playback. Qwen
supports Chinese, English, Japanese, Korean, German, French, Russian, Portuguese,
Spanish, and Italian, plus automatic language detection. Model capabilities drive
the controls; unsupported combinations are rejected before loading.

Generate uses a full-width left settings rail, central authoring surface and
saved-script rail. Its toolbar holds actual Qwen model controls, seed and output
processing. Magic turns support voice/language selection, direction, prosody,
pauses, substitutions, preview, regeneration, lock, download and reordering.
Switching between plain text and Magic preserves the text without adding dialogue.
Keep individual Magic turns within 400 characters; longer text can be synthesized
through the text/SSML modes with automatic splitting.

Save a named script to keep its document, settings, takes and current output in
the product volume. Imports/exports use SSML-H. Script folders, tags and search
organize the library. Saving remains explicit; ordinary editing and synthesis do
not automatically persist prompts or recordings. SSML-H `scope="profile"` is an
explicit instruction to persist a designed voice after successful generation.
See [SSML-H](SSML-H.md) for exact semantics and [API](API.md) for endpoint contracts.

Generation settings include temperature, top K, repetition penalty, chunk size,
maximum audio length, optional seed, and whole-text/incremental-text delivery.
Text delivery controls model input; streaming controls browser playback. These
are independent settings. The audio editor supports playback, volume, speed,
seeking, trimming, download, and sharing where supported by the browser.

Voice clone offers an optional **Delivery direction** field, such as "Speak slowly
and gently, with a reassuring tone." It is passed to the Base engine in both
complete and streaming generation. Choose **Speaker and reference transcript**
and supply the exact reference words for the recommended instruction path.
Base instruction following is experimental and can vary; identity-only cloning
may ignore the direction. This does not carry the same instruction-control
qualification as 1.7B CustomVoice. Leave it blank for ordinary voice cloning.
API clients use the existing `instruct` option alongside `mode: "clone"` and
`xvec_only: false`; capability metadata marks Base instruction support experimental.

Cloning defaults to **Speaker and reference transcript** with incremental text
input. Enter the exact words or use Transcribe reference. Select **Speaker identity
only** when a transcript is unavailable. Generate and Voice design default to
whole-text input. Explicit text-delivery choices stay with their workflow while
the page is open. Reset controls restores the current workflow's default.

The recording surface lets you select a microphone or use the system default.
Refresh the list after connecting hardware; browser permission reveals device
names. Device changes and permission errors are reported beside recording.
Audio chunk controls accept every integer from 1 to 64 codec frames and show
approximate audio duration. Playback streaming is independent of text input.

Metrics report audio length, first-audio latency, generation time, and
audio-seconds per generation-second. First-audio and generation timings begin
after model loading; reference preparation and audio decoding are included.
The API reports total inference time including queue wait and model loading.
Generation diagnostics distinguish queue wait, model loading, reference preparation
and cache reuse, streaming model TTFA/generation, browser first-chunk receipt,
scheduled playback start and live playback buffer. Model timings cover token
prefill/decode when reported; unavailable measurements are not estimated.
Breakdowns overlap and should not be summed. Scheduled playback does not measure
speaker hardware latency. Waiting requests show queue position and can be stopped.

Prepared voice prompts are reused by audio content, transcript and cloning settings
within the loaded model. An LRU cache retains at most eight entries and 8 MiB of
tensor data in system RAM. No raw recording is retained by this cache; uploaded
temporary files are deleted after inference. Unloading or switching the model
clears prepared references. Explicitly saved voices remain in the product volume.

Tab changes retain current work; reloading clears prompts and generated audio.
**Save voice** explicitly stores a reference and transcript in the product
volume. That library and ASR settings survive browser/container restarts. No
inherited reference recordings are bundled or fetched.

Only clone authorized speakers and process recordings you may use. Do not use
cloned voices for deceptive impersonation. A model license does not grant rights
to somebody else's identity or copyrighted input.

## Reference transcription

Connect an existing OpenAI-compatible service such as
[Qwen3-ASR-STT](https://github.com/hangry-labs/Qwen3-ASR-STT). Save or test its URL
in System. No ASR server runs inside this product, and no local ASR container is
launched for testing. A service on another machine leaves local VRAM for TTS.

`QWEN_STUDIO_ASR_URL` supplies the initial connection when no saved setting exists.
`task start` forwards this environment variable; saved System settings take
precedence. Leave the URL blank to disconnect. Reference audio is sent to the
chosen service only when Transcribe reference is pressed. Generation and manual
transcripts work without ASR.

## Ports and API

The UI and Studio API share **port 7860**, bound to loopback by default. For
another host interface, run `task start BIND_ADDRESS=0.0.0.0 PORT=7860`.
This local Studio has no account/login system. Microphone capture requires
localhost or HTTPS and browser permission. Its UI assets, fonts, and waveform
editor do not require a CDN.

Local API documentation is at `/docs`, with its schema at `/openapi.json`.
`/studio/capabilities` describes the
models, controls and limits. `/studio/generate` returns base64 WAV plus metrics;
`/studio/generate/stream` returns server-sent events carrying WAV chunks.
It also reports queue/loading progress. With `?streaming=false`, the same progress
route surrounds complete inference and returns one complete audio chunk; the
ordinary `/studio/generate` route retains its JSON response.
Both accept multipart data containing an `options` JSON field and an optional
`reference` audio file. Separate `/v1/audio/speech` and native `/tts/*` routes
provide the new product API. MCP is not implemented.

## Migration and checks

The Studio provides model selection, all three voice modes, custom speakers
and supported instructions, upload/recording, transcription, both cloning
methods, streaming/complete output, sampling controls and downloads. The saved
voice library replaces fixed operator reference slots. The six migration gaps
are closed; see the [migration review](UI_MIGRATION.md) for the comparison and
deliberate differences. The old UI and its launch/package integration have been
removed. Hosted Space login/quotas and the old GGML adapter are also removed;
the maintained engine is NVIDIA/Torch with local model source.

```powershell
task validate
task test-runtime
task smoke
task smoke -- --all-models
```

Smoke checks generate real GPU samples and transcribe them with the selected
ASR service. Audio/results are written under ignored `artifacts/studio-smoke/`.
Set `QWEN_STUDIO_ASR_URL` in your shell or an untracked `.env` file before running
Task, or pass `ASR_URL=https://asr.example.com` to `task smoke`. Direct script
invocations accept `--asr-url`. The smoke test requires an explicit connection;
it does not fall back to a local ASR service. Generated samples are sent to that
service for transcription.
These short correctness checks are not representative quality/speed benchmarks.
See [development tasks](DEVELOPMENT.md) and [licensing](LICENSING.md) for the
remaining dependency-lock and image-release work.
