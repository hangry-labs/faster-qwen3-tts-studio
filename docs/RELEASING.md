# Container builds and releases

The GitHub Actions workflow in
[docker-build.yml](../.github/workflows/docker-build.yml) follows the Hangry Labs
VoxCPMTTS full/tiny publishing pattern. It builds Linux amd64 NVIDIA/Torch images
and sends the same built indexes to both registries:

- Docker Hub: `hangrylabs/faster-qwen3-tts-studio`
- GHCR: `ghcr.io/hangry-labs/faster-qwen3-tts-studio`

The workflow is configured in source. Registry images become available after its
first successful publishing run. This document does not assert that a tag has
already been published.

## Triggers and tags

| Event | Full image | Tiny image |
| --- | --- | --- |
| Pull request | Validation only; no credentials or image publishing | Validation only |
| Push to `main` | `latest` | `latest_tiny` |
| Push stable `vX.Y` or `vX.Y.Z` Git tag | Matching version tag | Matching version plus `_tiny` |
| Manual dispatch | Selected stable tag and/or `latest` | Corresponding `_tiny` tags |

Snapshot or development version tags are not published. The local `:dev` image
remains a development convenience. Stable tags do not implicitly update rolling
tags. Manual dispatch exposes the same controls as the sibling workflow:

- `image_tag`: an existing stable Git tag, such as `v1.0` or `v1.0.1`.
- `checkout_ref`: optional commit/ref; defaults to `image_tag`, otherwise the
  workflow's selected ref. A versioned publication must check out the exact commit
  named by its stable Git tag.
- `push_latest`: defaults to true. Set false for a stable-only manual publication.
  Leave `image_tag` empty and use true for an explicitly selected rolling build.

Stable registry tags are checked before any image is published. If any selected
version tag already exists in either registry, the workflow fails instead of
moving it. This includes partially completed publications: inspect the existing
digests and failed run before choosing a recovery. Do not blindly rerun or move a
published tag. Authentication/network failures are not treated as proof of absence.

## Credentials

The names match VoxCPMTTS:

| Secret | Purpose |
| --- | --- |
| `DOCKER_USERNAME` | Docker Hub user with access to the `hangrylabs` repository |
| `DOCKER_TOKEN` | Docker Hub access token with push permission |
| `GITHUB_TOKEN` | Automatic Actions token used for GHCR with `packages: write` |

No separate GHCR personal access token is required by this workflow. Registry
login uses action inputs rather than interpolating credentials into shell code.
PR validation has read-only repository access and does not use publishing secrets.
On first publication, confirm the GHCR package is publicly pullable and associated
with this repository. Configure Docker Hub's repository as public as intended.

## What the build does

1. Check notices, publication rules, source/wheel contents and package metadata.
2. Record the validated commit and use that exact SHA in the publishing job.
3. Free disk space on the ephemeral hosted runner and configure Docker Buildx.
4. Validate release identity and select full/tiny tags.
5. Build the `checks` target and run CPU runtime tests without network access.
6. Build/publish `baked`, then `tiny`, with OCI source/revision/version/build-date
   labels, build provenance and SBOM attestations.
7. Inspect every selected registry tag and require its top-level OCI index digest
   to match the corresponding build result.
8. Export runtime notices and the model file manifest as an Actions artifact.

The full image contains all five pinned model snapshots and their upstream cards.
The asset build verifies model/tokenizer configuration and records file SHA-256
hashes. It does not load a model onto a GPU during image construction. Its startup
merges those snapshots into `HF_HOME`, preserving other downloaded models. Reuse
the same persistent product volume with full and tiny images. Initial full-image
startup copies model files into an empty cache; later starts reuse them.

Full defaults to `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. Tiny defaults to
online downloads into the volume. Neither variant includes a local ASR model.
Reference transcription still connects only to an operator-selected service.

The shared application stage stores installed Python/Debian notices and component
inventory under `/app/licenses/runtime`. The full image also contains the pinned
model manifest under `/app/baked-models/huggingface/model-manifest.json`, copied
into the cache during startup. The evidence artifact contains these records and
`published-images.json` with verified readable-tag/digest references.

Inventory collection is not legal approval. The [licensing audit](LICENSING.md#container-release-requirements)
still governs exact runtime/native dependencies, required corresponding source,
model provenance and release-image qualification. Core dependencies and the Python
base digest are pinned; the apt and transitive Python dependency tree is not yet
a complete artifact lock.

## Local validation

```powershell
task validate
task package
docker build --target checks .
docker build --target tiny -t faster-qwen3-tts-studio:tiny .
docker build --target baked -t faster-qwen3-tts-studio:full .
```

The default Dockerfile target is `tiny`, so `task init` retains its lightweight
model-cache workflow. Full and tiny have identical application code and runtime
dependencies. The full target inherits the model asset layer directly to keep
peak hosted-runner disk usage down. Its application install is constrained to
the exact dependency versions resolved in the shared app stage, recorded in
`/app/runtime-constraints.txt` and exported with the evidence.

The isolated CI builder uses [BuildKit cache settings](../.github/buildkitd.toml)
that reserve 40 GB for cache, allow up to 60 GB, and target 10 GB free space.
The model snapshots and NVIDIA dependencies together exceed small default cache
budgets. Keeping them through the full/tiny/evidence steps avoids downloading
the checkpoints repeatedly within one publishing job. These settings do not
change an operator's Docker daemon. Local full builds also need room for model
layers, compressed image blobs and an initial writable model-cache copy.

GitHub-hosted CPU runners do not qualify real GPU inference. Before promoting a
release, exercise the packaged candidate with NVIDIA hardware, full with a fresh
cache and no network, and tiny with an online cache fill followed by an offline
restart. Use an existing ASR service for the configured speech smoke checks.
Retain the exact candidate identity and review UI/API behavior and release notices.

## First release and documentation promotion

Choose the first Hangry Labs version deliberately and align package/UI version
metadata and release notes before creating its stable Git tag. The inherited
package version is not automatically promoted by this workflow. `task release`
still builds local Python artifacts; it does not create commits/tags or publish
images. The old upstream PyPI publisher has been removed.

After a successful run, verify full and tiny tags in both registries. Use the
top-level index digest from the workflow summary or `docker buildx imagetools
inspect`; do not substitute a platform child-manifest digest. Promote README and
Docker Hub examples to readable release tags plus those verified digests. Keep
moving `latest` examples unpinned. The workflow does not create a GitHub Release
page or upload the Docker Hub description automatically.

Buildx's [build/push action](https://github.com/docker/build-push-action) documents
the provenance/SBOM options; GitHub's
[secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use)
describes least-privilege tokens and pinned actions. Action references here are
pinned to commit SHAs.
