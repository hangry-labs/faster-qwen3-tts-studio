<p align="center">
  <a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/?lang=en">
    <img src="https://raw.githubusercontent.com/hangry-labs/faster-qwen3-tts-studio/main/src/faster_qwen3_tts/standalone_ui/assets/qwen3_tts_logo_horizontal.webp" alt="Hangry Labs Faster Qwen3-TTS Studio logo" width="900">
  </a>
</p>

<p align="center"><a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/?lang=en">English</a> · <a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/?lang=nb">Norsk bokmål</a> · <a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/?lang=pl">Polski</a> · <a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/?lang=ja">日本語</a> · <a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/?lang=zh">简体中文</a> · <a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/?lang=es">Español</a></p>

<p align="center"><a href="https://hangry-labs.github.io/faster-qwen3-tts-studio/examples/?lang=en"><strong>🎧 Listen to voice examples</strong></a></p>

# Hangry Labs Faster Qwen3-TTS Studio

Local voice design, reference cloning and expressive speech generation in one
Docker container, with a browser Studio, streaming audio, OpenAI-compatible APIs
and optional MCP tools.

**Publication status:** `v1.0`, `v1.0_tiny` and `v1.0_sources` are published on Docker Hub and GHCR. The commands below pin the verified matching OCI indexes.

## Quick Start

With Docker, NVIDIA GPU support and a CUDA 12.8-compatible driver installed, run:

```bash
docker run -d --name faster-qwen3-tts-studio --restart unless-stopped -p 127.0.0.1:7860:7860 --gpus all -e CUDA_VISIBLE_DEVICES=0 -v faster_qwen3_tts_studio_data:/app/persistent hangrylabs/faster-qwen3-tts-studio:v1.0@sha256:a8a3643b077e05c2ccf33e9b97978f082d2e89ac33b3d1368ab0e25df628899d
```

Open **http://localhost:7860**. API documentation is at **http://localhost:7860/docs**
and the schema is at **http://localhost:7860/openapi.json**.

The full image includes all five pinned checkpoints and can run offline after
the image pull. The named volume preserves models, saved voices and scripts.

For a smaller download, use the tiny image instead:

```bash
docker run -d --name faster-qwen3-tts-studio --restart unless-stopped -p 127.0.0.1:7860:7860 --gpus all -e CUDA_VISIBLE_DEVICES=0 -v faster_qwen3_tts_studio_data:/app/persistent hangrylabs/faster-qwen3-tts-studio:v1.0_tiny@sha256:29f06b3226da4a55244727e111e7700786e53049a54560efeef4bb12a62bd0bd
```

Tiny downloads its models into the same volume on first use. Keep it online
until the selected models are cached. Choose either full or tiny.

## Browser UI

<p align="center">
  <a href="https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/assets/screenshots/generate-ui.webp">
    <img src="https://raw.githubusercontent.com/hangry-labs/faster-qwen3-tts-studio/main/assets/screenshots/generate-ui.webp" alt="Qwen3-TTS Studio Generate workspace with Magic dialogue editing, voice settings and saved scripts" width="1200">
  </a>
</p>

## Image Variants And Tags

| Variant | Rolling tag | Stable release | Model assets |
| --- | --- | --- | --- |
| Full | `latest` | `v1.0` | All five pinned checkpoints baked in |
| Tiny | `latest_tiny` | `v1.0_tiny` | Download on first use |
| Sources | `latest_sources` | `v1.0_sources` | Corresponding-source archives and build recipes |

Both variants are built to `hangrylabs/faster-qwen3-tts-studio` and mirrored to
`ghcr.io/hangry-labs/faster-qwen3-tts-studio`. Full merges baked models into the
same persistent cache and defaults to offline use. Tiny needs network access
to populate its cache. Neither runs local ASR.

The Quick Start uses the published `v1.0` release with verified top-level OCI
index digests. GHCR uses the same tags and digests: replace `hangrylabs/faster-qwen3-tts-studio` with
`ghcr.io/hangry-labs/faster-qwen3-tts-studio` in either command.

`main` publishes the moving `latest` and `latest_tiny` tags. They remain unpinned
for users deliberately following development; see the
[version history](https://github.com/hangry-labs/faster-qwen3-tts-studio#version-history)
for those commands and fixed release references.

Matching source image: `hangrylabs/faster-qwen3-tts-studio:v1.0_sources@sha256:515ff1591aa438af475fb22deebb7b8efd619b6258d5f08ff5f12fb3b82b9831`.
Use the [corresponding-source guide](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/LICENSING.html#obtaining-corresponding-source)
to extract the archives and rebuild recipes without running an inference server.

## What You Get

- Create voices from descriptions with 1.7B VoiceDesign, then save them as cloning references
- Clone authorized recordings with 0.6B or 1.7B Base using reference audio and its transcript
- Choose nine built-in CustomVoice speakers, with style instructions on the 1.7B model
- Generate speech in ten languages, with automatic language selection
- Use incremental playback and live text-in/audio-out cloning with 1.7B Base
- Generate multi-character dialogue with Magic, a bounded SSML subset or SSML-H
- Organize saved voices with portraits, metadata, creation recipes and voice refinement
- Keep scripts and reusable takes, with long-text planning and FIFO queue progress
- Trim audio, compare original and processed previews, and apply optional effects and mastering
- Connect OpenAI-compatible speech/voice APIs or separately enabled compact and advanced MCP tools
- Choose per-workflow defaults and GPU residency, with timing and GPU telemetry in System
- Use the browser UI in English, Norwegian Bokmål, Polish, Japanese, Simplified Chinese or Spanish

The included offline gallery has ten designed voices, multilingual speech and
cloning comparisons, and downloadable voice recipes. Open **Examples** in the
Studio or use the listening link at the top of this page.

**Speech languages:** Chinese, English, Japanese, Korean, German, French, Russian,
Portuguese, Spanish and Italian. Interface language is independent of speech.

Base delivery direction remains experimental; transcript-assisted cloning is
recommended. The maintained Studio supports NVIDIA/Torch, with Python 3.13,
Torch 2.10.0 CUDA 12.8 wheels and locally maintained CUDA graph acceleration.
See [source provenance](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/UPSTREAMS.html)
for the three upstreams and incorporated revisions.

## Persistent Data And Runtime Settings

Reuse `faster_qwen3_tts_studio_data` at `/app/persistent` when replacing the
container. It holds downloaded checkpoints, compiler caches, operator settings
and explicitly saved reference voices. Deleting it removes those contents.
Uploads remain temporary unless explicitly saved; prompts and generated audio
are not automatically retained across browser reloads.

| Setting | Behavior |
| --- | --- |
| `CUDA_VISIBLE_DEVICES=0` | Select the first physical NVIDIA GPU; change the index as needed |
| `HF_HOME=/app/persistent/huggingface` | Downloaded model cache |
| `TORCHINDUCTOR_CACHE_DIR=/app/persistent/torch_inductor` | Compiler cache |
| `QWEN_STUDIO_DATA=/app/persistent/studio` | Operator settings and saved voices |
| `QWEN_STUDIO_ASR_URL` | Optional initial URL for an existing reference-transcription service |

ASR settings saved in **System > Reference transcription** override the initial
environment value. No local ASR model is included or started. You can enter
reference transcripts manually and generate speech without an ASR connection.

Memory needs vary by model and request. System can unload all weights while
keeping the UI available. Prepared clone prompts use a bounded CPU cache cleared
on unload. Inference is serialized with FIFO waiting-request feedback.

The example binds HTTP to this computer only. There is no account system.
`QWEN_STUDIO_API_KEY` optionally protects `/v1` with a Bearer key, but the native
and browser routes remain unauthenticated. Use trusted network controls if exposing
the port elsewhere. Recording requires localhost or HTTPS and browser permission.
Browser writes are restricted to the service host; direct API clients remain
supported without an `Origin` header.

## API Example

The Studio serves OpenAI-compatible speech, native generation, SSML/SSML-H,
Magic takes and saved voices/scripts on the same port. Opt-in compact and advanced
MCP endpoints are available at `/mcp/` and `/mcp/advanced/`; enable them in System.
For remote clients, set `QWEN_STUDIO_MCP_BASE_URL` to the reachable service origin.

```bash
curl http://localhost:7860/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-tts","input":"Good morning from Hangry Labs.","voice":"Ryan","response_format":"mp3"}' \
  --output speech.mp3
```

`GET /v1/models` and `/v1/audio/voices` expose the actual inventory. Saved voice
ids work with the speech endpoint, including optional delivery `instructions`.
Formats include MP3, WAV, FLAC, Opus, AAC, Ogg and raw 24 kHz mono PCM16.
OpenAI input remains plain text. Native `/tts/generate`, `/tts/stream` and
`/tts/events` support explicit `input_type="ssml"` or `"ssml-h"`.
See the [API guide](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/API.html)
and exact [SSML-H profile](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/SSML-H.html).

For LLM integrations, the [live speech API](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/LIVE_API.html)
accepts arriving text and returns PCM on `/tts/live`. It uses 1.7B Base and a saved
voice, including its reference transcript for full-reference cloning. Speaker-only
conditioning is also available. The service, UI and all APIs share port 7860.

Use this Python example with `httpx` installed:

```python
import base64
import json
from pathlib import Path

import httpx

options = {
    "mode": "custom",
    "model": "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    "text": "Good morning from Hangry Labs.",
    "speaker": "Ryan",
    "language": "English",
}
response = httpx.post(
    "http://localhost:7860/studio/generate",
    data={"options": json.dumps(options)},
    timeout=300,
)
response.raise_for_status()
Path("speech.wav").write_bytes(base64.b64decode(response.json()["audio_b64"]))
```

`GET /studio/capabilities` lists models, speakers, languages and limits.
`GET /studio/status` reports readiness, active model and queue state.
`POST /studio/generate/stream` returns server-sent events containing progress
and base64 WAV chunks. It is not a raw audio stream. Cloning accepts an uploaded
`reference` or saved `voice_id` alongside the multipart `options` JSON field.

## Responsible Use And Privacy

Only clone voices with the necessary consent and recording rights. Do not use
synthetic speech for deceptive impersonation, fraud or harassment. Review output
before publication, including commercial use.

Generation runs locally. First-use checkpoint downloads contact the model host.
Reference transcription sends audio to the operator-selected service only when
explicitly requested. Saved reference recordings remain in the product volume.

## Project Links

- [Project website and documentation](https://hangry-labs.github.io/faster-qwen3-tts-studio/)
- [GitHub repository and README](https://github.com/hangry-labs/faster-qwen3-tts-studio)
- [Studio guide](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/STUDIO.html)
- [Development tasks](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/DEVELOPMENT.html)
- [Container builds and releases](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/RELEASING.html)
- [Original accelerated engine](https://github.com/andimarafioti/faster-qwen3-tts)
- [Qwen3-TTS models and research](https://github.com/QwenLM/Qwen3-TTS)
- [Hangry Labs](https://hangrylabs.app/)

## Attribution And Licensing

The accelerated engine comes from Faster Qwen3-TTS by Andres Marafioti; Qwen
provides the model weights and core research. This independently maintained
Hangry Labs fork adds the Docker workflow, Studio and product integrations.
Streaming adaptations and the VoxCPMTTS-based UI retain their source notices.

The Python distribution is `MIT AND Apache-2.0`. Models and runtime dependencies
retain separate terms; a root permissive license does not replace those terms.
Images retain runtime component notices under `/app/licenses/runtime`.
Redistribution must also meet the applicable native-component and
corresponding-source requirements described in the licensing guide.

See [NOTICE](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/NOTICE),
[Third-Party Notices](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/THIRD_PARTY_NOTICES.md)
and the [licensing guide](https://hangry-labs.github.io/faster-qwen3-tts-studio/docs/LICENSING.html).
Report product issues in the
[GitHub issue tracker](https://github.com/hangry-labs/faster-qwen3-tts-studio/issues).
