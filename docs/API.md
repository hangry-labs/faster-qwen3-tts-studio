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

Optional extensions: `language`, `seed`, `voice_profile`, `normalize_loudness`.
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
MP3, PCM, Opus, AAC, FLAC or Ogg. Plain text without effects streams codec
chunks; markup/effected speech streams assembled speech units. Whole-recording
loudness normalization buffers the recording before output. One encoder owns
the entire response, preserving dialogue boundaries across compressed packets.

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

For uploaded cloning, send multipart `payload` JSON and `reference_audio` to
`/tts/generate-upload` or `/tts/stream-upload`. Set `mode="clone"`, `ref_text`
to the exact reference words, or `xvec_only=true` for identity-only conditioning.
Do not send server filesystem paths or remote audio URLs. For saved references,
set `voice_profile` to a saved id or unique name; the saved transcript is reused.

`protect_long_audio=true` splits at natural boundaries, up to 400 characters per
unit. With it disabled, each speech unit must fit 1000 characters. Requests are
bounded to 6000 spoken characters, 64 speech units and 300 seconds of final
audio. `max_new_tokens` applies per model call. Inspect the full plan before
inference with `POST /tts/plan`; `POST /tts/metrics` reports text and plan counts.

## Voices and saved scripts

`GET/POST /tts/voice-profiles` lists or explicitly saves references. POST takes
multipart `name`, `reference_audio`, optional `ref_text`, `language`,
`description`, JSON `tags`, and JSON `recipe`. PUT the same metadata to
`/tts/voice-profiles/{id}` to edit or replace reference audio. GET its `/audio`
child to download; DELETE the profile to remove it. Names must be unique.
Profiles remain compatible with the existing `/studio/voices` library.

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

| Routes | Purpose |
| --- | --- |
| `GET /tts/ping`, `/tts/status`, `/tts/activity` | Version, model and queue status |
| `GET /tts/defaults`, `/tts/formats`, `/tts/stream-formats` | Current defaults and encoding contracts |
| `GET /tts/languages`, `/tts/voices`, `/tts/speakers` | Qwen inventory and saved profiles |
| `GET /tts/ssml/capabilities` | Exact supported markup and processor limits |
| `POST /tts/transcribe-upload` | `reference_audio` forwarded to the configured ASR service |
| `POST /tts/postprocess-upload` | Audio plus JSON `options`: speed, pitch in semitones, linear volume, normalization, output format, and finishing controls below |
| `POST /tts/purge` | Unload this Studio's resident model |

Supply a unique `X-Qwen-Request-ID` (1 to 80 letters, digits or hyphens) with
`/tts/generate`, `/tts/stream`, `/tts/magic/take` or `/tts/magic/render`, then poll
`GET /tts/activity?request_id=...` for that request's phase, title and detail.
Completed progressive requests also expose metrics and committed profile ids.
Unknown or expired ids return an empty object. Progress is retained in memory
for up to an hour, bounded to the most recent 128 requests. Omitting the query
retains the model/queue status response.

Finishing accepts multipart `audio` and JSON `options`, up to 40 MB and 300
seconds. `method="ffmpeg"` offers `noise_reduction_db` (0 to 12), `bass_db` and
`presence_db` (-6 to 6), `dynamics` (0 to 100), and `normalize_loudness` (-16
LUFS). `method="ffmpeg-shape"` additionally applies `pitch_semitones` (-6 to 6)
and `speed_factor` (0.75 to 1.25). `preset` records `clean`, `studio` or `custom`;
clients send the numeric settings explicitly. Legacy `speed`, `pitch`, `volume`
and `output_format` remain supported. The browser keeps the original recording
separate from the processed preview.

The original `/studio/*` multipart/JSON/SSE contracts remain available for
single-model workflows. No local ASR, forced alignment, server-path audio access,
remote audio fetching, portrait upload or MCP service is added by these routes.
These are separate capabilities, rather than placeholders that claim success.
Only clone permitted speakers and use recordings you are authorized to process.
