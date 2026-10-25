# Development tasks

Use [Task](https://taskfile.dev/) v3, PowerShell 7 (`pwsh`),
[uv](https://docs.astral.sh/uv/), and Docker Desktop with Linux containers and
NVIDIA GPU support. The host does not need a Python virtual environment or CUDA
toolkit. `uv` supplies Python 3.13 for lightweight tooling; Docker holds the
inference dependencies.

Optional frontend regressions use Node.js 22 or newer and its built-in test
runner: `task test-ui`. They cover draft isolation across input modes and
overlapping audio loads without a browser, model download or npm dependencies.
The container publication workflow runs them before image builds. Interactive
Playwright checks against the running Studio complement these component tests.

```powershell
task doctor
task init
task start
# Open http://127.0.0.1:7860 and load a model in the UI.
task logs
task stop
```

## Build from source

For normal use, run a published image with the [one-command Quick Start](../README.md#quick-start).
To build a local tiny image from the source instead:

```bash
git clone https://github.com/hangry-labs/faster-qwen3-tts-studio.git
cd faster-qwen3-tts-studio
docker build -t faster-qwen3-tts-studio:dev .
docker volume create --label app.hangrylabs.project=faster-qwen3-tts-studio faster_qwen3_tts_studio_data
docker run -d --name faster-qwen3-tts-studio --restart unless-stopped -p 127.0.0.1:7860:7860 --gpus all -e CUDA_VISIBLE_DEVICES=0 -v faster_qwen3_tts_studio_data:/app/persistent faster-qwen3-tts-studio:dev
```

The default build downloads models on first use. Use `--target baked` when
building a full image with all five pinned checkpoints included.

## Main commands

| Command | Behavior |
| --- | --- |
| `task init` | Build the local development image from this checkout and create its persistent volume. Re-run after dependency or Dockerfile changes. |
| `task start` | Recreate this project's container, mount local source read-only, and wait up to 45 seconds for the status endpoint. Models download when requested in the UI. |
| `task stop` | Stop the container and retain the image, model cache, and other product data. Safe when already absent. |
| `task nuke` | Remove this project's labelled container, development image, and **all contents of its data volume**, including cached models and assets. Source files stay in place. |
| `task package` | Build wheel/sdist artifacts and check their notices and metadata. |
| `task release DRY_RUN=1` | Validate snapshot/stable/next-snapshot document transformations in memory without mutation. |
| `task release` | Validate and create local release/next-snapshot commits and an annotated source tag; never push or publish. |
| `task lock-runtime` | Compile the complete Linux/Python 3.13 NVIDIA wheel-hash lock. `CHECK=1` checks existing pins without changing the lock. |

The development image uses Python 3.13 and matching Torch 2.10.0 CUDA
12.8 wheels. It installs the current checkout and serves the
[Hangry Labs Studio](STUDIO.md) with Torch as the only enabled backend.
No model weights are baked into the development image. By default, startup
loads 0.6B Base, 0.6B CustomVoice and 1.7B VoiceDesign into GPU memory.
Change per-workflow defaults and residency in System.

`requirements.runtime.in` declares the supported runtime inputs;
`requirements.runtime.txt` locks their transitive versions and distribution hashes
for CPython 3.13/Linux x86-64/CUDA 12.8. Docker installs binary wheels with
`--require-hashes`, then installs local source without resolving additional
dependencies or creating a floating build environment. The Python base image is
pinned by digest; apt packages remain moving inputs. This local workflow does not qualify an image for release;
see [the licensing guide](LICENSING.md#container-release-requirements).

## Settings

Override Task variables on the command line. Use the same resource overrides
with subsequent lifecycle commands so they address the same image/container/data.

```powershell
task start PORT=7870 GPU_DEVICE=0
task start DEV_MOUNT=0
task nuke DRY_RUN=1
task --list
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `IMAGE` | `faster-qwen3-tts-studio:dev` | Local development image tag |
| `CONTAINER` | `faster-qwen3-tts-studio` | Container name |
| `DATA_VOLUME` | `faster_qwen3_tts_studio_data` | Unified persistent product volume |
| `PORT` | `7860` | Host HTTP port |
| `BIND_ADDRESS` | `127.0.0.1` | Host IPv4 interface; local access by default |
| `GPU_DEVICE` | `0` | Host NVIDIA GPU index |
| `DEV_MOUNT` | `1` | Mount local source; `0` runs the source packaged in the image |
| `DRY_RUN` | `0` | `1` previews lifecycle changes or release transformations without mutation |

If an optional `HF_TOKEN` is already set in the environment, `task start` passes
it through without putting the token value into the command line. Keep tokens
out of checked-in files.

The data volume is mounted at `/app/persistent`, containing the Hugging Face
cache, compiler cache, and explicit Studio voice library/settings. Restart the
container with `task start` after editing source; automatic reload is disabled.
The lifecycle script refuses to change resources owned by another project and
never runs Docker-wide prune commands. `nuke` leaves shared BuildKit cache alone.

The local Studio has no login screen. Use `BIND_ADDRESS` to choose its host
interface. Browser recording requires localhost or HTTPS and permission. Use
only reference recordings you may process and speakers who have authorized
cloning. Do not use cloned voices for deceptive impersonation.

## Validation and release preparation

`task smoke` generates real GPU samples and checks their text with an existing
ASR service. Set `QWEN_STUDIO_ASR_URL` in your shell or an untracked `.env` file,
or pass `ASR_URL=https://asr.example.com` to the task. No local ASR container is
launched. `-- --all-models` also covers both 1.7B CustomVoice and Base. This
inference is separate from lightweight validation. See [the Studio guide](STUDIO.md).

```powershell
task status
task validate
task test-runtime
task package
task release DRY_RUN=1
```

`task test` covers task lifecycle safety with a fake Docker command and licensing.
It does not install Torch on Windows, run model
inference, or measure GPU performance. After `task init`, `task test-runtime`
runs the remaining CPU engine unit tests in an ephemeral container, including
local model/codec compatibility checks and fresh offline Studio startup. It installs pytest only in that temporary
container and excludes model parity tests. GPU parity tests and benchmarks
remain separate work requiring appropriate model assets.

`task release` requires a clean, synchronized `main` and an unused stable version.
It promotes `VERSION`, Python package/runtime versions and README history, creates
an annotated local release tag, then commits the next development snapshot.
`NEXT_VERSION=1.1-snapshot` selects the next snapshot explicitly.
`SKIP_VALIDATION=1` reuses prior exact-candidate qualification; the default runs
validation, packaging and checks/full/tiny image builds. This is local preparation:
no push, PyPI upload or registry publication occurs. Publication is a separate
authorized action through the [container workflow](RELEASING.md).
