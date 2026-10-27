# Licenses and model terms

The Python distribution combines MIT and Apache-2.0 source. Model weights,
native libraries and other container dependencies retain their own terms.
Read [LICENSE](../LICENSE), [NOTICE](../NOTICE) and
[Third-Party Notices](../THIRD_PARTY_NOTICES.md) for the original grants
and attribution. The complete Docker image is not covered by one MIT grant.

## Decisions for the official Qwen models

| Question | Finding | Conditions |
| --- | --- | --- |
| May the weights be baked into Docker images? | Yes, under the reviewed Apache-2.0 grants | Retain the license, provenance and supplied notices; identify modifications/conversions; review the image's independent runtime components |
| May the software/model be used commercially? | Yes, under the reviewed MIT and Apache-2.0 grants | Preserve each component's terms; no claim that the entire runtime is MIT |
| May generated speech be used commercially? | No separate noncommercial, output royalty, or mandatory output-attribution restriction was found in the reviewed Qwen licenses | Input text, reference recordings, speaker consent, publicity/privacy rights, third-party expression and applicable law remain independent; the license does not guarantee output ownership or uniqueness |
| May paid hosted inference be offered? | Yes at the reviewed code/model-license level | No model-license ban on charging for inference was found; service launch still needs actual runtime, customer-data, voice-provenance, and operational review |

These are license-scope findings, not a warranty that every possible output or
business use is lawful. No permission for celebrity imitation or unauthorized
cloning follows from an open model license. Software copyright, model weights,
voice recordings, and generated recordings are separate objects of review.

The finding applies to these exact official repositories, including their
embedded Qwen speech-tokenizer assets:

| Repository | Reviewed revision | Declared license |
| --- | --- | --- |
| [`Qwen/Qwen3-TTS-12Hz-0.6B-Base`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base/blob/5d83992436eae1d760afd27aff78a71d676296fc/README.md) | `5d83992436eae1d760afd27aff78a71d676296fc` | Apache-2.0 |
| [`Qwen/Qwen3-TTS-12Hz-1.7B-Base`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base/blob/fd4b254389122332181a7c3db7f27e918eec64e3/README.md) | `fd4b254389122332181a7c3db7f27e918eec64e3` | Apache-2.0 |
| [`Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice/blob/85e237c12c027371202489a0ec509ded67b5e4b5/README.md) | `85e237c12c027371202489a0ec509ded67b5e4b5` | Apache-2.0 |
| [`Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice/blob/0c0e3051f131929182e2c023b9537f8b1c68adfe/README.md) | `0c0e3051f131929182e2c023b9537f8b1c68adfe` | Apache-2.0 |
| [`Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign/blob/5ecdb67327fd37bb2e042aab12ff7391903235d3/README.md) | `5ecdb67327fd37bb2e042aab12ff7391903235d3` | Apache-2.0 |
| [`Qwen/Qwen3-TTS-Tokenizer-12Hz`](https://huggingface.co/Qwen/Qwen3-TTS-Tokenizer-12Hz/blob/7dd38ad4e9bad454aae9cd937d0cd577604fe229/README.md) | `7dd38ad4e9bad454aae9cd937d0cd577604fe229` | Apache-2.0 |

Model cards at the linked immutable revisions define the scope of these
findings. The Studio pins its five TTS checkpoints to the listed revisions;
the standalone tokenizer entry records the codec publisher's declaration.

[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) grants reproduction,
derivation and distribution rights in sections 2 and 3, with redistribution
conditions in section 4 and trademark limits in section 6. No research-only,
noncommercial, revenue-threshold, or output-royalty clause was found in the
reviewed official cards. This finding does not extend to arbitrary Qwen-family
models, fine-tunes, conversions, or future revisions.

## Source and runtime licenses

The accelerated wrapper retains its MIT license. Local Qwen inference,
compatibility and adapted streaming source retain Apache-2.0 obligations.
The package expression `MIT AND Apache-2.0` describes combined source,
not a choice between those licenses. Incorporated revisions are recorded in
[upstream provenance](UPSTREAMS.md); source headers and notices are preserved.

Runtime dependencies include independently licensed Python and native code.
For example, Python-SoXR/libsoxr carries LGPL-2.1-or-later terms; certifi, tqdm
and portions carried by orjson include MPL-covered material. NVIDIA CUDA
libraries retain their own redistribution terms. Refer to the component
notices and inventory shipped with the exact image rather than applying the
project license to all its dependencies.

## Container release requirements

Container builds retain project notices, installed Python/Debian notices
and a component inventory under `/app/licenses/runtime`. Full images also
retain upstream model cards and record hashes for their pinned assets.
Inventory collection alone is not a legal approval of the combined image.

Redistribution must preserve applicable licenses, copyright and change
notices, and any required corresponding source, build materials or
replacement/relinking rights. Requirements depend on the actual components,
build/linking choices and modifications. An external FFmpeg process does not
automatically relicense independent application source or generated audio;
an MIT root license also does not remove GPL/LGPL distribution obligations.

Python runtime distributions are version- and hash-locked in
`requirements.runtime.txt`, and the Python base image is pinned by digest.
Debian apt inputs remain moving dependencies. Review the exact
distributed payload and its original terms. See
[container builds](RELEASING.md) and [Third-Party Notices](../THIRD_PARTY_NOTICES.md).

## Obtaining corresponding source

The publishing workflow creates a matching source image before application
images. Its application images include an `app.hangrylabs.sources` label
pointing to that source image in the same public registry repository.
The source reference includes the Git commit and workflow run/attempt: rebuilding
the same commit with different Debian inputs creates a different source reference.
Stable releases also publish `vX.Y_sources` (or `vX.Y.Z_sources`); moving builds
publish `latest_sources`. Use the exact reference from your application image,
since a moving source tag may describe a newer build.

After pulling the application image, inspect it and read `app.hangrylabs.sources`
under `Config.Labels`:

```bash
docker image inspect hangrylabs/faster-qwen3-tts-studio:latest
```

Substitute that source reference for `SOURCE_IMAGE` below. The source image is
a file archive, not an application to start; creating a stopped container lets
Docker copy its contents without running anything:

```bash
docker create --name qwen3-sources SOURCE_IMAGE /unused
docker cp qwen3-sources:/sources ./qwen3-sources
docker rm qwen3-sources
```

Docker Hub and GHCR carry the same source index. The equivalent GHCR reference
uses `ghcr.io/hangry-labs/faster-qwen3-tts-studio` with the same source tag.
Source images must remain available while distributing their matching binaries;
temporary CI evidence artifacts are not the source-delivery mechanism.

The archive includes:

- Exact Debian source packages, including descriptors, upstream archives,
  distribution patches and build scripts, for every installed Debian package.
- Reviewed wheel-bundled GCC runtime sources with their distribution patches and
  specifications; SoundFile's libsndfile and static codec sources/build recipe;
  the Python-SoXR archive containing its patched libsoxr; certifi and tqdm sources.
- Installed notices, native-file identities, build inputs, `manifest.json` and
  `SHA256SUMS`. Source files are verified against signed apt indexes or reviewed
  SHA-256 pins. No downloaded source is executed during collection.

Collectors fail when an exact Debian source is unavailable or a reviewed wheel
version/bundled binary changes. Update the review and source inputs rather than
substituting a newer upstream release. Local builds can produce the same archive
with `task sources`; local images labelled `local-build` do not claim a published
source reference. From the repository, verify the collected source-file hashes:

```bash
python scripts/collect_runtime_sources.py --verify --output qwen3-sources
```

### Replacement and rebuilding

GPL/LGPL/MPL-covered components retain their original rights. No project term
prohibits modifying them or debugging modifications to the LGPL components.
The application uses FFmpeg as a separate executable and replaceable native
libraries through ordinary dynamic loading. A derived image can replace an
interface-compatible library or executable; no application signature check locks
these components to the original bytes.

SoundFile's LGPL libsndfile is a separate shared library in `_soundfile_data`;
its archive includes the statically incorporated codec sources and build recipe.
The Python-SoXR extension includes LGPL libsoxr statically. Its complete wrapper,
patched library, headers and CMake/build configuration are included so users can
rebuild and replace the extension together. The GCC runtime exception covers
eligible application linking; it does not remove the bundled runtime libraries'
own source/notice requirements. Component build instructions and original license
texts in the archive take precedence over this summary.

NVIDIA and Intel binary components retain their separate redistribution terms.
These proprietary terms are not applied to the independent GPL/LGPL/MPL source.
In particular, Torch includes Intel oneMKL 2024.2.0 under the
[Intel Simplified Software License](../THIRD_PARTY_NOTICES.md#intel-onemkl-license-text).
The source archive is not a promise of a bit-for-bit rebuild of every proprietary
component, and collection success does not automatically approve a future image.

## Reference audio and generated speech


No inherited reference recordings or local ASR model are distributed. The
Studio starts with an empty saved-voice library. Optional transcription sends
audio only to the configured independent service when requested.

Only use text and recordings you may process, and obtain the necessary
speaker consent. Keep provenance and permissions for saved voices and
published samples. An open model license does not grant rights to another
person's identity or copyrighted input.

## Notice checks

```bash
python scripts/check_licensing.py
python -m unittest discover -s tests -p test_licensing.py -v
python scripts/check_licensing.py --artifact dist/package.whl --artifact dist/package.tar.gz
```

Use Python 3.13 and substitute the actual artifact names. These checks verify
notice preservation and package contents; they do not certify an independently
assembled image or infer usage rights from an SPDX identifier alone.
