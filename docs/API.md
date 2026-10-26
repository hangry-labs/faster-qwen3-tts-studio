# Speech API

The UI, native API and OpenAI-compatible speech API share port **7860**, one
FIFO inference queue and the same local Qwen implementation. Discover the exact
request schemas at `/openapi.json`. The browser API guide is `/docs`.

## OpenAI-compatible clients

```bash
curl http://localhost:7860/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-tts","input":"Good morning from Hangry Labs.","voice":"Ryan","response_format":"mp3"}' \
  --output speech.mp3
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:7860/v1", api_key="local")
with client.audio.speech.with_streaming_response.create(
    model="qwen3-tts", voice="Ryan", input="Good morning from Hangry Labs.",
    response_format="mp3",
) as response:
    response.stream_to_file("speech.mp3")
```

`GET /v1/models` lists the five actual checkpoints. `GET /v1/models/{id}` also
accepts the routing aliases `qwen3-tts`, `faster-qwen3-tts`, `tts-1`, `tts-1-hd`
and `gpt-4o-mini-tts`. These aliases select Qwen workflows, not OpenAI models.
With an alias, a saved voice selects 0.6B Base; native voice instructions select
1.7B CustomVoice; otherwise native voices select 0.6B CustomVoice. An explicit
Qwen checkpoint must match the requested workflow and supported instructions.

`GET /v1/audio/voices` lists native speakers, compatibility aliases and saved
profile ids. OpenAI voice aliases such as `alloy` map to documented Qwen
speakers; they do not reproduce OpenAI voices. A saved voice works as either
its id, unique name or `{"id":"saved-id"}`. `instructions` directs delivery,
including experimental Base delivery with an audio-backed saved voice.

Formats: MP3 (default), WAV, FLAC, Opus in Ogg, AAC in ADTS, Ogg Vorbis, and raw
PCM. PCM is **24 kHz, mono, signed 16-bit little endian, with no header**.
WAV and FLAC complete before delivery; other formats use one progressive
encoder. OpenAI `stream_format="audio"` is supported. OpenAI speech SSE events
are not implemented. `input` is always plain text; use native routes for markup.
`speed` is a pitch-preserving audio effect, from 0.25 to 4.0.

Optional extensions include `language`, `seed`, `randomize_seed`, `voice_profile`,
`normalize_loudness`, `protect_long_audio`, `temperature`, `top_k`,
`repetition_penalty`, `chunk_size`, `decoder_context_frames`, `max_new_tokens`, `non_streaming_mode`
and `xvec_only`. They use the same validation and controls as native requests.
Unknown harmless OpenAI fields are ignored. Unsupported formats, voices,
models and conditioning combinations return OpenAI-shaped error objects.
Set `QWEN_STUDIO_API_KEY` to require a Bearer key on `/v1` routes. This does
not authenticate the browser, native API or System routes; use a trusted bind
address or an authenticated reverse proxy for the whole Studio.

## Native synthesis

```bash
curl http://localhost:7860/tts/generate \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hello again.","voice":"Ryan","seed":42,"output_format":"wav"}' \
  --output speech.wav
```

`POST /tts/generate` and `/tts/convert` return complete binary audio. Use
`POST /tts/stream` for a progressive response and select `stream_format` from
MP3, PCM, Opus, AAC, FLAC or Ogg. All three Qwen model families produce
incremental codec audio. Text and multi-turn SSML/SSML-H can stream within each
speech unit. Internal boundary compaction retains up to 600 ms of audio at a
unit edge; it does not wait for the next unit to finish. Explicit pauses and
outer recording edges retain the complete-response semantics.

Speed/prosody use a continuous filter per speech unit. Optional loudness
normalization runs once over the assembled stream. These filters and compressed
codecs add buffering, so browser playback latency differs from model/SSE TTFA.
One encoder owns the entire response. MP3 uses bounded input probing to avoid
waiting for the whole short recording. If MP3 MediaSource is unavailable, the
browser collects the stream and plays the completed recording instead.

`POST /tts/events` returns native SSE progress and base64 WAV chunks, followed
by a `done` event containing metrics and committed profile ids. This is separate
from the OpenAI protocol. Cancelling/disconnecting stops queued work and asks
active generation to stop at its next yield. An in-flight complete model call
finishes before releasing its GPU lease.

All native routes accept `input_type="text"` (default), `"ssml"` or `"ssml-h"`.
See the [processor profile](SSML-H.md). `instruct`, `control` and `instructions`
are equivalent names for a default delivery/voice description. Sampling controls
are `temperature`, `top_k`, `repetition_penalty`, `seed`, `max_new_tokens`,
`chunk_size` and `non_streaming_mode`. The last field controls Qwen text input,
independently of response streaming. Qwen does not have VoxCPM diffusion steps,
guidance, denoising or continuation controls; native unknown fields fail clearly.

`decoder_context_frames` controls how many preceding codec frames are reused
when reconstructing streamed audio. It accepts integers from 1 to 200 and defaults
to 25 in every voice mode. Larger windows may improve continuity but require more
decoder work and memory. It is independent of chunk size, sampling and text
conditioning, and has no effect on complete waveform generation. Use it on native
streaming routes or as an OpenAI extension with a progressive format such as PCM
or MP3; OpenAI WAV/FLAC responses use complete generation.

For uploaded cloning, send multipart `payload` JSON and `reference_audio` to
`/tts/generate-upload` or `/tts/stream-upload`. Set `mode="clone"`, `ref_text`
to the exact reference words, or `xvec_only=true` for identity-only conditioning.
Do not send server filesystem paths or remote audio URLs. For saved references,
set `voice_profile` to a saved id or unique name; the saved transcript is reused.

### Long text

`protect_long_audio=true` is the default. The planner counts words in spaced
scripts and characters in CJK scripts, preferring sentence endings, then clauses,
then whitespace, with a hard 400-character ceiling. Default planning targets
50 units with an 80-unit ceiling; smaller codec budgets reduce those limits.
Whitespace is collapsed and an uninterrupted oversized word is split at the
character ceiling. These heuristics do not guarantee speech duration.
With protection disabled, each speech unit must fit 1000 characters.

Native source input can contain up to 50000 characters, including markup;
OpenAI `input` is limited to 4096. Both use the processor limits of 6000 spoken
characters, 64 compiled speech units and 300 seconds of final audio. The audio
limit is enforced during execution, including pauses and effects, so an
overlong stream can fail after some audio has already been delivered.

Each split is a fresh model call with the chosen voice/reference and a seed
incremented by speech-unit index. Previous chunks are not supplied as narration
context. Clone calls reuse the original reference; VoiceDesign repeats the
description for each chunk. New SSML-H voice definitions are bootstrapped
before dialogue synthesis starts. One FIFO GPU lease covers the whole request.

Internal padding is compacted and adjacent speech receives a 120 ms handoff;
an explicit SSML break replaces that gap. Outer recording edges are preserved.
Streaming still retains audio for the completed result and takes; it is not a
constant-memory long-form session.

`max_new_tokens` applies per model call, not to the final joined recording.
The default 360 codec frames represent roughly 30 seconds of raw speech;
the maximum 600 represents roughly 50 seconds, before effects. Exhausting the
token or model-context budget is reported as incomplete generation. Complete
native responses may retry the affected unit once in up to three smaller
sections before publishing audio; `metrics.retries` records this recovery.
A failed retry returns HTTP 422. Streaming never regenerates already-emitted
speech: SSE reports an error and binary streams terminate unsuccessfully.
There is no automatic continuation from partial model context.

Inspect the full plan before inference with `POST /tts/plan`;
`POST /tts/metrics` reports text and plan counts. The legacy `/studio/generate`
and `/studio/generate/stream` routes, used by the dedicated Design/Clone
workflows, accept at most 1000 text characters in one model call and do not use
this automatic splitting. Audio output streaming requires the complete input
request first; incremental text input and bidirectional sessions are not exposed.

## Voices and saved scripts

`GET/POST /tts/voice-profiles` lists or explicitly saves references. POST takes
multipart `name`, `reference_audio`, optional `ref_text`, `language`,
`description`, JSON `tags`, JSON `recipe`, and `profile_type` (`clone`, `reference`
or `design`). Names are unique ignoring case. `GET /tts/voice-profiles?q=warm`
searches names, descriptions, tags and languages.

Optional `original_audio`, `processed_audio` and `design_audio` uploads retain
the creation recording, processed alternative and source cloning reference.
Audio is stored as mono float WAV without changing its sample rate. Each upload
must fit the reference limits: 10 MB and two minutes. The selected
`reference_audio` is what synthesis uses. `portrait` accepts PNG/JPEG/WebP up to
5 MB and 25 megapixels, normalized to a 100×100 lossless WebP.

PUT metadata to `/tts/voice-profiles/{id}` to edit it. Omitted fields, audio and
creation assets remain intact. Replacing `reference_audio` requires
`replace_audio=true`; send the replacement creation assets alongside it.
Unspecified processed/source recordings are cleared on audio replacement to
avoid retaining an unrelated creation history. Portraits persist unless replaced
or explicitly removed with `clear_portrait=true`. POST `replace=true` also allows
explicit replacement by an existing unique name, preserving its profile id.

Responses include `audio_url`, optional `original_url`, `processed_url`,
`source_url` and `portrait_url`, plus recipe and timestamps. GET these URLs to
retrieve assets; DELETE `/tts/voice-profiles/{id}` removes the profile and assets.
Old saved voices and `/studio/voices` remain compatible. Recipes record creation
settings; matching a seed alone does not guarantee identical audio across model
or runtime changes.

`GET/POST /tts/dialogue-scripts`, `GET/PUT/DELETE /tts/dialogue-scripts/{id}`,
and GET its `/download` child manage SSML-H scripts. Scripts contain a `name`,
`document`, optional `description`, `tags` and `folder`. Script storage validates
markup without requiring every referenced voice to be installed yet. Synthesis
resolves all voices before taking the GPU lease.

`POST/DELETE /tts/dialogue-script-folders[/{id}]` creates/deletes folders.
`PATCH /tts/dialogue-scripts/{id}/folder` moves a script. Deleting a folder
leaves its scripts ungrouped. `POST /tts/dialogue-workspaces` and
`PUT /tts/dialogue-workspaces/{id}` explicitly store a script, settings, locked
takes and optional output/processed audio. They take multipart `metadata`,
`takes`, `output` and `processed`; the browser sends this contract when saving.
Stored audio is validated and canonicalized to WAV, with a 20 MB per-file and
40 MB total upload limit. Script/workspace data stays in the product volume.

## Magic

Magic compiles the same SSML-H plan as native synthesis. It adds take editing:

| Route | Request | Response |
| --- | --- | --- |
| `POST /tts/magic/take` | JSON `payload` speech request and zero-based `speech_index` | One WAV take; never commits document profiles |
| `POST /tts/magic/render` | Multipart `payload`, ordered JSON `speech_ids`, JSON `retained` id/seed records, matching `takes` files | Generated/unlocked takes plus assembled output |
| `POST /tts/magic/assemble-upload` | Multipart JSON `options` timeline, `take_metadata`, `takes` | Assemble existing takes without inference |

Render returns `application/vnd.hangrylabs.magic-takes`: a four-byte little
endian JSON manifest length, UTF-8 manifest, then audio payloads. Manifest
version 1 describes each take/output offset and length relative to the audio
payload, seed, format and committed profiles. The packaged `magic-takes.js`
client implements this shared Hangry Labs contract. Speech ids correspond to
compiled units; keep Magic turns within 400 characters to avoid automatic splits.
Locked takes are reused byte-for-byte at WAV precision. Source editing invalidates
the browser's corresponding take. Assembly preserves explicit positive/zero
pauses and adds a 120 ms handoff only where no pause was specified.

## Discovery and utilities

Operator model defaults live at `GET /system/settings` under `model_policy`.
`PUT /system/settings` accepts either `asr_url`, `model_policy`, or both, preserving
other settings. A policy contains `enabled` and all three `workflows` keys:
`custom`, `clone`, `design`, each with a compatible full `model` id and a
`keep_loaded` boolean. Disabling `enabled` releases weights after each request;
it preserves per-workflow choices. Changes apply without a container restart.
`GET /studio/status` lists actual `resident_models`, requested pins and individual
`residency_errors`. Its `gpu_memory` reports this process's PyTorch allocated and
reserved MiB once CUDA is initialized, independently of device-wide telemetry.
A saved policy may need more VRAM than the GPU has available;
inspect status after applying it. `GET /studio/capabilities` exposes workflow defaults.
Explicit request model ids override defaults; interoperable aliases and `auto`
use them. CustomVoice delivery direction automatically selects a capable 1.7B
model when the configured 0.6B default cannot accept instructions.

| Routes | Purpose |
| --- | --- |
| `GET /tts/ping`, `/tts/status`, `/tts/activity` | Version, model and queue status |
| `GET /tts/defaults`, `/tts/formats`, `/tts/stream-formats` | Current defaults and encoding contracts |
| `GET /tts/languages`, `/tts/voices`, `/tts/speakers` | Qwen inventory and saved profiles |
| `GET /tts/ssml/capabilities` | Exact supported markup and processor limits |
| `POST /tts/transcribe-upload` | `reference_audio` forwarded to the configured ASR service |
| `POST /tts/postprocess-upload` | Audio plus JSON `options`: speed, pitch in semitones, linear volume, normalization, output format, and finishing controls below |
| `POST /tts/purge` | Unload all models in this Studio |

Supply a unique `X-Qwen-Request-ID` (1 to 80 letters, digits or hyphens) with
`/tts/generate`, `/tts/stream`, `/tts/magic/take` or `/tts/magic/render`, then poll
`GET /tts/activity?request_id=...` for that request's phase, title and detail.
Completed progressive requests also expose metrics and committed profile ids.
Unknown or expired ids return an empty object. Progress is retained in memory
for up to an hour, bounded to the most recent 128 requests. Omitting the query
retains the model/queue status response.

Finishing accepts multipart `audio` and JSON `options`, up to 40 MB and 300
seconds. `method="ffmpeg"` provides noise cleanup, EQ, dynamics and optional
loudness normalization. `ffmpeg-shape` and `signalsmith` add independent
`pitch_semitones` (-6 to 6) and `speed_factor` (0.75 to 1.25).
WAV previews use float samples at Qwen's native 24 kHz rate.

Advanced controls include `high_pass_hz`, `warmth_db`/`warmth_hz`,
`mud_db`/`mud_hz`, `presence_db`/`presence_hz`, `air_db`/`air_hz`,
`compression_ratio`, `compression_threshold_dbfs`, `compression_attack_ms`,
`compression_release_ms`, `deesser_strength_percent`, `saturation_blend_percent`,
`room_percent`, `target_loudness_lufs` and `peak_ceiling_dbtp`. The schema exposes
exact bounds; the air band tops out at 11 kHz for the 24 kHz signal.
Loudness normalization remains opt-in. `preset` records `clean`, `studio` or
`custom`; clients send numeric settings explicitly. Legacy `speed`, `pitch`,
`volume` and `output_format` remain supported. Originals and processed previews
remain separate, and preview processing does not load TTS weights.

The original `/studio/*` multipart/JSON/SSE contracts remain available for
single-model workflows. Native speech requests may provide `ref_audio` as a
container path within the configured MCP input directory. It is mutually
exclusive with an upload or `voice_profile`. `POST /tts/transcribe` accepts JSON
`{"audio_location":"reference.wav"}` from that same directory. Native routes do
not fetch URL references; bounded HTTP inputs belong to advanced
[MCP tools](MCP.md). No local ASR or forced alignment is bundled.
Only clone permitted speakers and use recordings you are authorized to process.

`GET /tts/ping` and `/tts/status` include `version`, `build_id`, `build_date` and
`image_version`. Unspecified development build metadata is reported as `unknown`;
runtime does not infer a Git revision from the host filesystem.

## Queue admission

GPU inference remains serialized. `QWEN_STUDIO_QUEUE_SIZE` sets pending capacity
from 0 to 256, default 8. The synthesis pipeline admits at most this value plus
one request, including requests still finishing CPU audio work. Zero permits one
request at a time, including its finishing stage.
Native and OpenAI generation reserve admission before voice lookup and plan
compilation, which run off the HTTP event loop while earlier requests synthesize.
Reference files are prepared before the GPU lease. Model tokenization, reference
encoding and waveform decoding still run under that lease.
Admission happens before creating a generation thread or opening a response
stream. A full queue returns HTTP 429 with `Retry-After: 1`; `/v1` uses an
OpenAI error envelope. Cancellation removes queued work. Status includes queue
capacity, active/waiting counts, total synthesis `inflight` and cumulative rejected
admissions. Full-response per-unit effects run on CPU workers with at most two
unfinished units per request and two simultaneous effect operations per service.
The final model call releases the GPU before assembly and whole-recording
normalization. Streaming releases it before the final filter drain; bounded
stream buffers still apply backpressure during inference. HTTP encoding already
runs separately from GPU inference.

Native generation metrics add `preparation_ms`, `gpu_lease_ms` and
`postprocess_ms`. Preparation measures off-loop voice lookup and compilation.
The GPU lease includes model preparation and synthesis; the CPU tail starts
after release and excludes HTTP encoding. These intervals can overlap work from
other requests. `queue_ms` measures time until GPU acquisition, including
reference file preparation; `total_ms` starts after planning. Complete-response
`ttfa_ms` remains time to assembled audio, rather than a streaming latency claim.
