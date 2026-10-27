# Container builds and image tags

The [container workflow](../.github/workflows/docker-build.yml) builds Linux
amd64 NVIDIA/Torch images for Docker Hub and GHCR:

- `hangrylabs/faster-qwen3-tts-studio`
- `ghcr.io/hangry-labs/faster-qwen3-tts-studio`

Registry images become available after a successful publishing run. The workflow
configuration does not itself establish that a particular tag is available.

## Tags

| Source | Full image | Tiny image |
| --- | --- | --- |
| Push to `main` | `latest` | `latest_tiny` |
| Stable `vX.Y` or `vX.Y.Z` Git tag | Matching version | Matching version plus `_tiny` |

Pull requests run validation without publishing. Manual dispatch can select a
stable tag and/or rolling tags. Snapshot version tags are not published. Stable
tags are checked for existing publications; the workflow rejects replacement.
Both registries receive the same built OCI indexes, checked after publication.
Each build also publishes a matching source image before publishing application
images. Source tags include `latest_sources`, stable `vX.Y_sources`/`vX.Y.Z_sources`,
and a unique `sources-<commit>-<run>-<attempt>` identity. Application image labels
reference the unique source identity so later rebuilds cannot silently replace it.

For reproducible deployment, use a published readable tag with its verified
top-level OCI index digest. Rolling tags intentionally remain unpinned.
Published deployment references belong in the [README version history](../README.md#version-history).

## Image contents

Full and tiny contain the same application and runtime dependencies. Full adds
all five pinned checkpoints, seeds them into the persistent Hugging Face cache
without deleting other downloads, and defaults to offline operation. Tiny
downloads missing checkpoints into that cache. Both reuse `/app/persistent`.
Neither includes a local ASR model.

Images carry OCI source, revision, version and build-date labels, plus runtime
notices under `/app/licenses/runtime`. The workflow exports component inventories,
model file hashes, source manifests and verified image references as build evidence. License and
source obligations are described in [licensing](LICENSING.md#container-release-requirements).

## Local builds

```powershell
task validate
task package
docker build --target checks .
docker build --target sources -t faster-qwen3-tts-studio:sources .
docker build --target tiny -t faster-qwen3-tts-studio:tiny .
docker build --target baked -t faster-qwen3-tts-studio:full .
```

The default Dockerfile target is `tiny`. Full builds require additional disk
space for model assets and an initial writable cache copy. CPU checks do not
qualify GPU synthesis or offline model loading. Python dependencies are fully
version/hash locked for the supported runtime; apt inputs remain separate.

## Snapshot promotion

```powershell
task release DRY_RUN=1
# After reviewing and qualifying the candidate:
task release
```

Dry run validates both stable and next-snapshot transformations entirely in memory,
including README history, package/runtime versions and the Docker Hub publication
notice. It does not fetch, build, write files or create refs, and can inspect a
dirty checkout. A real promotion requires clean `main`, synchronized with
`origin/main`, and an unused stable tag. It creates a local release commit,
annotated `vX.Y`/`vX.Y.Z` tag and next-snapshot commit. It never pushes or publishes.

The default runs only lightweight `task validate` checks. Release preparation
does not build packages or Docker images. Qualify runtime behavior during
development; GitHub Actions performs package checks and image builds when the
prepared refs are pushed. Use `NEXT_VERSION=1.1-snapshot` to choose a newer next
version, or `SKIP_VALIDATION=1` to reuse the lightweight checks when already run.
If promotion stops after a release commit, inspect local refs before retrying;
do not move a published tag.

When publication is separately authorized, the prepared refs can be pushed
atomically with `git push --atomic origin main vX.Y`. The tag workflow builds the
stable images; `main` builds the next moving snapshot. After registry verification,
add top-level index digests to README history before announcing availability.
See [development tasks](DEVELOPMENT.md) for other commands.
