<p align="center">
  <a href="https://hangrylabs.app/">
    <img src="https://raw.githubusercontent.com/hangry-labs/faster-qwen3-tts-studio/main/src/faster_qwen3_tts/standalone_ui/assets/qwen3_tts_logo_horizontal.webp" alt="Hangry Labs Faster Qwen3-TTS Studio logo" width="900">
  </a>
</p>

# Hangry Labs Faster Qwen3-TTS Studio

Local Qwen3-TTS voice design, reference cloning and speech generation with a
browser Studio, streaming playback and an HTTP API.

**Publication status:** the full/tiny build and publishing workflow is configured
for Docker Hub and GHCR. Tags become available after its first successful run.
The source-build commands below work before that publication.

## Project Links

- [GitHub repository and README](https://github.com/hangry-labs/faster-qwen3-tts-studio)
- [Studio guide](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/docs/STUDIO.md)
- [Development tasks](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/docs/DEVELOPMENT.md)
- [Container builds and releases](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/docs/RELEASING.md)
- [Original accelerated engine](https://github.com/andimarafioti/faster-qwen3-tts)
- [Qwen3-TTS models and research](https://github.com/QwenLM/Qwen3-TTS)
- [Hangry Labs](https://hangrylabs.app/)

## Quick Start

Use Docker with Linux containers, NVIDIA GPU support and a driver compatible
with CUDA 12.8. Build the development image from source:

```bash
git clone https://github.com/hangry-labs/faster-qwen3-tts-studio.git
cd faster-qwen3-tts-studio
docker build -t faster-qwen3-tts-studio:dev .
docker volume create --label app.hangrylabs.project=faster-qwen3-tts-studio faster_qwen3_tts_studio_data
docker run -d --name faster-qwen3-tts-studio --restart unless-stopped -p 127.0.0.1:7860:7860 --gpus all -e CUDA_VISIBLE_DEVICES=0 -v faster_qwen3_tts_studio_data:/app/persistent faster-qwen3-tts-studio:dev
```

Open **http://localhost:7860**. API documentation is at **http://localhost:7860/docs**
and the schema is at **http://localhost:7860/openapi.json**.

Model weights download into the named volume. They are not baked into this
development image. The Studio keeps 0.6B Base, 0.6B CustomVoice and 1.7B VoiceDesign
ready by default. In System, choose each workflow's default and whether it stays
loaded, or disable keeping weights to release them after each complete request.

## Image Variants And Tags

| Variant | Rolling tag | Stable release | Model assets |
| --- | --- | --- | --- |
| Full | `latest` | `vX.Y` or `vX.Y.Z` | All five pinned checkpoints baked in |
| Tiny | `latest_tiny` | Matching stable version plus `_tiny` | Download on first use |

Both variants are built to `hangrylabs/faster-qwen3-tts-studio` and mirrored to
`ghcr.io/hangry-labs/faster-qwen3-tts-studio`. Full merges baked models into the
same persistent cache and defaults to offline use. Tiny needs network access
to populate its cache. Neither runs local ASR.

`main` builds rolling tags; stable Git tags build fixed releases. After publishing,
stable installation commands will use the verified tag and top-level OCI digest.
The current commands intentionally use the local `:dev` target.

## What You Get

- VoiceDesign 1.7B for voices described in natural language
- Base 0.6B and 1.7B for cloning authorized reference recordings
- Optional experimental Base delivery direction; transcript-assisted cloning recommended
- CustomVoice 0.6B and 1.7B with nine built-in speakers; style instructions on 1.7B
- Complete WAV generation and incremental playback
- Upload, drag and drop, microphone selection, recording and waveform trimming
- Explicitly saved voice profiles and generated-design reuse for cloning
- Optional reference transcription through an existing ASR service
- Queue progress, cancellation, timing diagnostics and content-based prompt reuse
- System controls for per-workflow defaults, model residency and GPU telemetry
- Python 3.13 with Torch 2.10.0 CUDA 12.8 wheels

**Languages:** Chinese, English, Japanese, Korean, German, French, Russian,
Portuguese, Spanish and Italian, plus automatic selection.

The maintained Studio supports NVIDIA/Torch. CUDA graph acceleration uses the
official Qwen checkpoints with locally maintained inference code. See
[source provenance](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/docs/UPSTREAMS.md)
for all three upstreams and exact incorporated revisions.

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

## API Example

The Studio serves OpenAI-compatible speech, native generation, SSML/SSML-H,
Magic takes and saved voices/scripts on the same port. MCP is not implemented.

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
See the [API guide](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/docs/API.md)
and exact [SSML-H profile](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/docs/SSML-H.md).

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

## Attribution And Licensing

The accelerated engine comes from Faster Qwen3-TTS by Andres Marafioti; Qwen
provides the model weights and core research. This independently maintained
Hangry Labs fork adds the Docker workflow, Studio and product integrations.
Streaming adaptations and the VoxCPMTTS-based UI retain their source notices.

The Python distribution is `MIT AND Apache-2.0`. Models and runtime dependencies
retain separate terms; a root permissive license does not replace those terms.
The development image still needs exact dependency, native-component and
corresponding-source qualification before release distribution.

See [NOTICE](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/NOTICE),
[Third-Party Notices](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/THIRD_PARTY_NOTICES.md)
and the [licensing guide](https://github.com/hangry-labs/faster-qwen3-tts-studio/blob/main/docs/LICENSING.md).
Report product issues in the
[GitHub issue tracker](https://github.com/hangry-labs/faster-qwen3-tts-studio/issues).
