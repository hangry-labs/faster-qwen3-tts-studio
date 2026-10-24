<p align="center">
  <img src="src/faster_qwen3_tts/standalone_ui/assets/qwen3_tts_logo_horizontal.webp" alt="Hangry Labs Faster Qwen3-TTS Studio logo" width="900">
</p>

# Hangry Labs Faster Qwen3-TTS Studio

Development version **v1.0-snapshot**. See the [release notes](docs/RELEASE_NOTES.md).

Local Qwen3-TTS voice design, voice cloning and speech generation in a Docker
Studio with a browser UI, streaming playback and an HTTP API.

Describe a new voice, turn it into a cloning reference, or generate speech with
one of Qwen's built-in speakers. This Hangry Labs fork brings those workflows
together with audio editing, saved voices and NVIDIA GPU controls.

## Quick Start

**Current status:** the [full/tiny container workflow](docs/RELEASING.md) is
configured for Docker Hub and GHCR. Registry images become available after its
first successful publishing run. You can build and run this checkout now:

Install Git, Docker with Linux containers and NVIDIA GPU support, and a driver
compatible with CUDA 12.8. No host Python environment or CUDA toolkit is needed.

```bash
git clone https://github.com/hangry-labs/faster-qwen3-tts-studio.git
cd faster-qwen3-tts-studio
docker build -t faster-qwen3-tts-studio:dev .
docker volume create --label app.hangrylabs.project=faster-qwen3-tts-studio faster_qwen3_tts_studio_data
docker run -d --name faster-qwen3-tts-studio --restart unless-stopped -p 127.0.0.1:7860:7860 --gpus all -e CUDA_VISIBLE_DEVICES=0 -v faster_qwen3_tts_studio_data:/app/persistent faster-qwen3-tts-studio:dev
```

Open **[http://localhost:7860](http://localhost:7860)**. Generate loads the selected
model on demand. First use downloads its pinned checkpoint into the persistent
volume; model weights are not baked into this development image.

The same port serves the [API view](http://localhost:7860/docs) and
[OpenAPI schema](http://localhost:7860/openapi.json). It includes OpenAI-compatible
speech, native synthesis, SSML/SSML-H, Magic takes and saved voices/scripts.
See the [API guide](docs/API.md). MCP is not implemented yet.

On Windows, the [Task workflow](docs/DEVELOPMENT.md) provides `task init`,
`task start` and `task stop` instead of assembling Docker commands manually.

## What You Get

- Description-based voice design with the 1.7B VoiceDesign model
- Reference cloning with 0.6B or 1.7B Base, including optional delivery direction
- Nine built-in CustomVoice speakers, with style instructions on the 1.7B model
- Ten languages plus automatic language selection
- Complete WAV output or incremental browser playback
- OpenAI-compatible speech in MP3, WAV, FLAC, Opus, AAC, Ogg and PCM
- Magic dialogue editing, a bounded SSML subset and SSML-H designed characters
- Saved script folders, locked/reusable takes and explicit workspace snapshots
- Reference upload, drag and drop, microphone selection and recording
- Waveform playback, trimming, download and browser-supported sharing
- An explicit saved-voice library that survives container replacement
- Optional reference transcription through an existing ASR service
- FIFO generation progress, cancellation, timing diagnostics and bounded prompt reuse
- On-demand model loading/unloading and GPU telemetry in System
- Python 3.13, Torch 2.10.0 and CUDA 12.8 wheels in the development image

The product targets **NVIDIA GPUs with the Torch backend**. It keeps one TTS
model resident at a time and serializes inference.

## Browser UI

| View | What you can do |
| --- | --- |
| Generate | Choose a built-in speaker, enter text and generate speech. Use 1.7B for style instructions. |
| Voice design | Describe a voice, generate a sample, then reuse or save it as a cloning reference. |
| Voice clone | Upload, record or choose a saved voice; supply its transcript and optional delivery direction. |
| API | Inspect capabilities, request formats and available routes. |
| System | Load or unload models, configure reference transcription and inspect GPU activity. |

Cloning defaults to **speaker and reference transcript**. Enter the exact words
or use the explicit Transcribe reference action. Speaker-identity-only cloning
is also available when no transcript exists.

Base delivery direction is experimental and can vary by voice and instruction.
Transcript-assisted cloning is recommended; identity-only cloning may ignore
direction. CustomVoice 0.6B does not accept style instructions.

The UI includes sampling controls, exact chunk size, seed, maximum audio length,
and independent text-input and playback-streaming choices. See the
[Studio guide](docs/STUDIO.md) for workflow details and timing definitions.

## Models And Languages

| Model family | Sizes | Purpose |
| --- | --- | --- |
| Base | 0.6B, 1.7B | Clone a reference voice; optional experimental delivery direction |
| CustomVoice | 0.6B, 1.7B | Generate with nine built-in speakers; instructions on 1.7B |
| VoiceDesign | 1.7B | Create a voice from a natural-language description |

**Languages:** Chinese, English, Japanese, Korean, German, French, Russian,
Portuguese, Spanish and Italian, plus Auto.

The Studio uses five fixed official Qwen checkpoint revisions. Faster inference
comes from the engine's CUDA graph execution and caching, using the same model
checkpoints. See the [model revisions and licenses](docs/LICENSING.md).

## Docker Reference

### Image And GPU Selection

`faster-qwen3-tts-studio:dev` is the local tiny target built above. The publishing
workflow builds these variants to `hangrylabs/faster-qwen3-tts-studio` and
`ghcr.io/hangry-labs/faster-qwen3-tts-studio`:

| Variant | Rolling tag | Stable tag | Models |
| --- | --- | --- | --- |
| Full | `latest` | `vX.Y` or `vX.Y.Z` | All five pinned checkpoints included |
| Tiny | `latest_tiny` | Matching version plus `_tiny` | Download into the volume on first use |

These tags are publication rules, not a claim that the first run has finished.
Full seeds its baked files into the same model cache used by tiny and defaults
to offline operation. See [container builds and releases](docs/RELEASING.md) and
the prepared [Docker Hub description](docs/dockerhub.md).

Change `CUDA_VISIBLE_DEVICES=0` to another physical GPU index when needed. Allow
headroom for other GPU workloads; memory needs depend on the selected checkpoint
and request. System can unload the resident TTS model without stopping the UI.

The default port mapping binds to this computer only. The Studio has no account
system. An optional `QWEN_STUDIO_API_KEY` protects only `/v1` routes. Publish the
whole Studio to a trusted network only with appropriate
access controls. Browser microphone capture needs localhost or HTTPS and
permission.

### Persistent Data And Settings

Mount one volume at `/app/persistent` and reuse it when replacing the container.

| Location | Contents |
| --- | --- |
| `/app/persistent/huggingface` | Downloaded model checkpoints |
| `/app/persistent/torch_inductor` | Compiler cache |
| `/app/persistent/studio` | Settings, explicitly saved voices, scripts and workspace audio |

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `CUDA_VISIBLE_DEVICES` | Set to `0` in the quick start | Select the visible NVIDIA GPU |
| `QWEN_STUDIO_ASR_URL` | Empty | Initial connection to an existing reference-transcription service |
| `QWEN_STUDIO_API_KEY` | Empty | Optional Bearer key for OpenAI-compatible `/v1` routes only |
| `QWEN_STUDIO_DATA` | `/app/persistent/studio` | Operator settings and saved-voice directory |
| `HF_HOME` | `/app/persistent/huggingface` | Model download cache |
| `TORCHINDUCTOR_CACHE_DIR` | `/app/persistent/torch_inductor` | Compiler cache |

Configure ASR in **System > Reference transcription**. Saved settings take
precedence over the environment default. The Studio does not run a local ASR
model; generation and manual transcripts work without a transcription service.

Uploaded references are temporary unless explicitly saved. Prepared clone
prompts are cached by content in system RAM, bounded to eight entries and 8 MiB
of tensor data, and cleared on model unload. Browser prompts and generated
outputs are not automatically saved across page reloads.

### Stop Or Replace The Container

```bash
docker stop faster-qwen3-tts-studio
docker start faster-qwen3-tts-studio
```

To use a rebuilt image, stop and remove the container, then rerun the quick-start
`docker run` command with the same named volume. Removing the volume deletes
cached models, settings and saved voices.

## API Usage

Discover models and controls with `GET /studio/capabilities`. Generation accepts
multipart form data with an `options` JSON field and, for cloning, a `reference`
audio upload or saved `voice_id`.

```bash
curl http://localhost:7860/studio/capabilities
```

With `httpx` installed in your client environment, this Python example requests
a built-in voice and saves the returned WAV:

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

The complete response contains `audio_b64`, `sample_rate` and `metrics`.
`POST /studio/generate/stream` returns server-sent events with progress and
base64 WAV chunks. It is not a raw audio byte stream. Use `?streaming=false`
for queue/loading progress around a complete generation.

| Route | Purpose |
| --- | --- |
| `GET /studio/status` | Readiness, active model and queue state |
| `GET /studio/capabilities` | Models, speakers, languages, controls and limits |
| `POST /studio/generate` | Complete generation as JSON with base64 WAV |
| `POST /studio/generate/stream` | Generation progress and WAV chunks as SSE |
| `GET /studio/voices` | Explicitly saved voice profiles |
| `POST /studio/models/load` | Load an official checkpoint |
| `POST /studio/models/unload` | Release the active model |

The [Studio guide](docs/STUDIO.md) covers the browser and existing multipart
contracts. The [speech API guide](docs/API.md) covers OpenAI-compatible clients,
native binary/streaming output, voice saving, Magic and script workspaces.

```bash
curl http://localhost:7860/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-tts","input":"Good morning from Hangry Labs.","voice":"Ryan","response_format":"mp3"}' \
  --output speech.mp3
```

For structured dialogue, opt in with `input_type="ssml"` or `"ssml-h"` on native
routes. Read the exact [SSML-H processor profile](docs/SSML-H.md); this is a
bounded subset, not complete W3C SSML support. OpenAI input stays plain text.

## Local Development

Install Task v3, PowerShell 7 and uv alongside Docker. Heavy runtime dependencies
stay in the container.

```powershell
task init
task start
task stop
task release
```

`task start` mounts local source read-only; `task start DEV_MOUNT=0` uses only the
packaged image. `task validate` checks syntax, lifecycle safety and notices;
`task test-runtime` runs CPU unit tests in Docker. `task smoke` exercises real
generation against an explicitly configured ASR service.
With Node.js 22 or newer installed, `task test-ui` checks input-mode isolation
and audio replacement races without loading a model.

`task release` prepares local Python artifacts; it does not publish a Docker
release. `task nuke` deletes this project's container, local image and **all data
in its volume**. Core versions are pinned, but the development build is not a
complete transitive Python/apt artifact lock. See [development tasks](docs/DEVELOPMENT.md).

## Benchmarks And Engine Reference

The Studio has real GPU generation/transcription smoke checks, not a qualified
Hangry Labs performance benchmark suite yet. The
[inherited benchmark tables](docs/UPSTREAM_BENCHMARKS.md) are upstream results
and should not be presented as measurements of this Docker build.

[Engine and Python reference](docs/ENGINE.md) covers the inherited library/CLI,
streaming, clone conditioning and parity tests. These details are secondary to
the maintained Docker Studio workflow.

## Upstream Project And This Fork

[Faster Qwen3-TTS](https://github.com/andimarafioti/faster-qwen3-tts) by Andres
Marafioti provides the accelerated inference engine. The
[Qwen team](https://github.com/QwenLM/Qwen3-TTS) provides the model family and
core research. We maintain its inference implementation locally, including the
Transformers 5 fixes from
[andimarafioti/Qwen3-TTS](https://github.com/andimarafioti/Qwen3-TTS/tree/distribution/qwen-tts-hf).
These are our three ongoing upstreams; [source provenance and synchronization](docs/UPSTREAMS.md)
records exact revisions, package boundaries and the update procedure. Both the
model and accelerated engine ship from this checkout, without an external Qwen
inference package or Gradio demo. Streaming adaptations also draw from
[Qwen3-TTS-streaming](https://github.com/dffdeeq/Qwen3-TTS-streaming), with CUDA
graph inspiration acknowledged from
[nano-qwen3tts-vllm](https://github.com/tsdocode/nano-qwen3tts-vllm).

Hangry Labs maintains this fork's Docker workflow, standalone Studio, audio
tools, saved voices, service integration and validation. The UI builds on the
Hangry Labs [VoxCPMTTS](https://github.com/hangry-labs/VoxCPMTTS) shell. Upstream
model authors retain credit for their weights and research.

## Support And Issues

Report bugs and feature requests in
[this repository's issue tracker](https://github.com/hangry-labs/faster-qwen3-tts-studio/issues).
Include reproduction steps, container logs, GPU/driver information and the model
and settings involved. Remove tokens, private recordings and personal information
before sharing logs.

## Responsible Use And Privacy

Only clone speakers with the necessary consent and recording rights. Do not use
synthetic voices for deceptive impersonation, fraud or harassment. Check generated
speech before publication, including commercial use.

Generation runs locally. First-use model downloads contact the model host.
Reference transcription sends audio to the configured ASR service only when
explicitly requested. Saved voices retain reference recordings in the product
volume; do not share that volume or recordings without authorization.

## License

The original wrapper retains its MIT license; adapted Qwen/streaming portions
retain Apache-2.0 obligations. The Python distribution is described as
`MIT AND Apache-2.0`. Model weights and Docker dependencies retain their own
licenses; the complete runtime is not covered by a single MIT grant.

Read [LICENSE](LICENSE), [NOTICE](NOTICE),
[Third-Party Notices](THIRD_PARTY_NOTICES.md) and the
[licensing audit](docs/LICENSING.md) for model redistribution, commercial-use
findings and remaining release-image qualification work.
