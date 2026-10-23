# Development tasks

Use [Task](https://taskfile.dev/) v3, PowerShell 7 (`pwsh`),
[uv](https://docs.astral.sh/uv/), and Docker Desktop with Linux containers and
NVIDIA GPU support. The host does not need a Python virtual environment or CUDA
toolkit. `uv` supplies Python 3.13 for lightweight tooling; Docker holds the
inference dependencies.

```powershell
task doctor
task init
task start
# Open http://127.0.0.1:7860 and load a model in the UI.
task logs
task stop
```

## Main commands

| Command | Behavior |
| --- | --- |
| `task init` | Build the local development image from this checkout and create its persistent volume. Re-run after dependency or Dockerfile changes. |
| `task start` | Recreate this project's container, mount local source read-only, and wait up to 45 seconds for the status endpoint. Models download when requested in the UI. |
| `task stop` | Stop the container and retain the image, model cache, and other product data. Safe when already absent. |
| `task nuke` | Remove this project's labelled container, development image, and **all contents of its data volume**, including cached models and assets. Source files stay in place. |
| `task release` | Run local validation, build wheel/sdist artifacts in `dist/`, and verify their notices and metadata. Remote publication is not configured yet. |

The development image uses Python 3.13 and matching Torch/TorchAudio 2.10.0 CUDA
12.8 wheels. It installs the current checkout and uses the existing FastAPI
demo with Torch as the only enabled backend. No model weights are baked in;
starting the container does not preload models.

`requirements.dev.txt` pins the core runtime components. It is not a complete
transitive lockfile. The base image and apt dependencies also remain moving
development inputs. This local workflow does not qualify an image for release;
see [the licensing audit](LICENSING.md#container-release-requirements).

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
| `DRY_RUN` | `0` | `1` prints Docker mutations without executing them |

If an optional `HF_TOKEN` is already set in the environment, `task start` passes
it through without putting the token value into the command line. Keep tokens
out of checked-in files.

The data volume is mounted at `/app/persistent`, containing the Hugging Face
cache, compiler cache, demo assets, and optional usage database. Restart the
container with `task start` after editing source; automatic reload is disabled.
The lifecycle script refuses to change resources owned by another project and
never runs Docker-wide prune commands. `nuke` leaves shared BuildKit cache alone.

The existing local demo has authentication disabled. Exposing it beyond the
default loopback interface requires deployment and access-control work. Use
only reference recordings you may process and speakers who have authorized
cloning. Do not use cloned voices for deceptive impersonation.

## Validation and release preparation

```powershell
task status
task validate
task test-runtime
task package
task release
```

`task test` covers task lifecycle safety with a fake Docker command, licensing,
and lightweight demo behavior. It does not install Torch on Windows, run model
inference, or measure GPU performance. After `task init`, `task test-runtime`
runs the remaining CPU engine unit tests in an ephemeral container, including
the mocked GGML adapter tests. It installs pytest only in that temporary
container and excludes model parity tests. GPU parity tests and benchmarks
remain separate work requiring appropriate model assets.

`task release` currently prepares **local Python artifacts**. It does not tag,
commit, push, upload to PyPI, or publish Docker images. The inherited upstream
PyPI workflow is not the Hangry Labs Studio release procedure. A future Docker
release workflow needs version policy, registries, pinned dependencies, exact
image validation, and corresponding-source delivery before publication.
