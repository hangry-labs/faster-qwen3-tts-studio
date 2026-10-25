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
model file hashes and verified image references as build evidence. License and
source obligations are described in [licensing](LICENSING.md#container-release-requirements).

## Local builds

```powershell
task validate
task package
docker build --target checks .
docker build --target tiny -t faster-qwen3-tts-studio:tiny .
docker build --target baked -t faster-qwen3-tts-studio:full .
```

The default Dockerfile target is `tiny`. Full builds require additional disk
space for model assets and an initial writable cache copy. CPU checks do not
qualify GPU synthesis or offline model loading. Core versions are pinned, but
the apt and transitive Python inputs are not a complete artifact lock.

`task release` prepares local Python artifacts; it does not create Git refs or
publish images. See [development tasks](DEVELOPMENT.md) for local commands.
