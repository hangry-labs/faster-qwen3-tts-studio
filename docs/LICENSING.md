# Licensing and commercial-use audit

Reviewed 2026-10-23 against source baseline `1094aab`, the model revisions below,
and 121 candidate Python artifacts. This is a source/model audit; a final
runtime image still needs review against its exact installed components.

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

Source declarations can be independently fetched from each linked model card
at its reviewed revision. The audit fetched cards/configuration and
repository metadata, not multi-gigabyte tensor files. Immutable revisions and
reviewed cards identify the scope; they do not mean the current loaders already
pin downloads to those revisions.

[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) grants reproduction,
derivation and distribution rights in sections 2 and 3, with redistribution
conditions in section 4 and trademark limits in section 6. No research-only,
noncommercial, revenue-threshold, or output-royalty clause was found in the
reviewed official cards. This finding does not extend to arbitrary Qwen-family
models, fine-tunes, conversions, or future revisions.

## Findings and repairs

### Adapted source was not accurately described by MIT alone

`model.py` explicitly identifies its local Talker input construction as a copy
of upstream Qwen logic. The README also credits adapted streaming code from
`dffdeeq/Qwen3-TTS-streaming`. Both upstreams use Apache-2.0. A root MIT file
does not remove those obligations.

Repairs: preserve the original MIT license; add NOTICE and Apache texts;
identify the adapted portions in source headers; declare `MIT AND Apache-2.0`
for the Python distribution; include the license material in source and wheel
artifacts. This is a mixed-source license expression, not a dual-license choice.

### Hidden Python and native dependencies matter

The inherited metadata resolved to 118 distributions for a Linux x86-64/Python
3.13 licensing research candidate. Three additional optional wheels were
inspected separately, for 121 total artifact inspections. Wheel notices were
read through bounded ZIP range requests, without installing or executing their
code. Recorded whole-wheel hashes are publisher declarations; only
retained notice bytes and the downloaded source archives were independently
hashed. This distinction is intentional.

The candidate is not a validated dependency set or an installation lock. In
particular, an apparently successful resolver result does not prove TorchAudio
binary compatibility with a floating Torch version. No Python/CUDA migration
or model inference was performed as part of licensing research.

Findings include:

- The former `qwen-tts-hf` dependency brought Gradio for an unused demo. The
  model source is now local and the demo/dependency are removed.
- Librosa brings Python-SoXR/libsoxr, under LGPL-2.1-or-later.
- MPL-covered components include certifi, tqdm, and portions carried by orjson.
- Package labels alone miss native payloads and vendored code, including
  numerical runtimes and NVIDIA libraries.
- Some wheels omit license files. Missing notices must be supplied from the
  applicable upstream, not treated as permission to discard attribution.
- The inherited demo's unconstrained apt/pip installs could not identify a final
  release's exact payload in advance.

Dependency notices belong with the exact installed distributions in the image.
Use the runtime collector for a repeatable follow-up against that actual build.
See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) for component detail,
supplemental notices, and the Apache-2.0 text. Research candidate notices and
source archives are not shipped as if they qualified the eventual runtime.

### Local inference source and removed optional runtimes

The model implementation and Transformers 5 compatibility changes are now
maintained in this repository under their original Apache-2.0 terms. Exact
revisions and all three synchronization sources are recorded in
[upstream provenance](UPSTREAMS.md). Original source headers are retained and
the modified 12 Hz wrapper/export/version files identify local changes. The
existing accelerated wrapper retains its MIT and adapted Apache obligations.

The unused Gradio demo, 25 Hz codec, GGML/native adapter and local-ASR benchmark
utilities have been removed. The runtime does not install `qwen-tts-hf`,
Gradio, ONNX Runtime, Python SoX or TorchAudio. Historical candidate inventories
describe the old dependency set, not the current container. Reference
transcription uses a separately configured service and bundles no ASR assets.

### Historical recordings were not cleared by the code license

Three source reference WAVs and 32 generated comparison WAVs had no independently
documented recording/speaker provenance or specific generated-media grant in
the reviewed materials. They were removed from the current distribution.
Demo auto-downloads were initially disabled; the old demo and preset loader have
since been removed. The Studio starts with an empty explicit voice library and
does not fetch inherited recordings. Public examples no longer embed removed audio.

This is a provenance gap, not a claim that the original publisher infringed a
right. Existing Git history and old upstream artifacts were not rewritten.
New examples should use a documented original recording or a newly generated
voice with an explicit redistribution grant and recorded recipe.

## Container release requirements

The current [container workflow](RELEASING.md) pins the Python base image by
digest, includes a runtime notice inventory and builds full/tiny targets. The
full target records hashes for its pinned model files and retains upstream model
cards. A supplemental Apache notice for the inspected Tokenizers wheel without a
license file is recorded in [Third-Party Notices](../THIRD_PARTY_NOTICES.md#supplemental-notices-for-installed-wheels).
These packaging records support the exact-image review below; they are not a
substitute for it.

There is no newly qualified Hangry Labs Studio image from this audit. The
now-retired demo recipe used Python 3.10, floating installs, a package version
different from the checkout, Ubuntu media tools and NVIDIA runtimes. Its build
and deployment instructions were not a production release approval. The current
Python 3.13 development image still requires the exact release review below.

For the eventual pinned Python 3.13/NVIDIA candidate:

1. Pin the base image digest, Python and Python-package artifacts, model
   revisions, native components, and build inputs. Record the actual payload.
2. Preserve this project's notices and each dependency's original notice files.
   Run `scripts/collect_runtime_licenses.py` inside the exact final image.
3. Inspect apt binary/source identities, FFmpeg build flags, libsndfile,
   libsoxr, codec libraries, GCC runtimes and exceptions, and optional CUDA or
   FlashAttention payloads. Include exact necessary source and build/patch
   materials and provide required replacement/relinking rights.
4. Match CUDA/cuDNN libraries to their own redistribution permissions and
   preserve their terms. [NVIDIA's CUDA terms](https://docs.nvidia.com/cuda/eula/index.html)
   license identified distributable portions under specific conditions; they
   do not make the whole SDK unrestricted open-source software.
5. Use only reviewed model revisions with their cards, licenses, provenance
   and change notices. Do not ship the removed reference media.
6. Verify notices/source are actually present in the finished image and
   downloadable distribution. A passing source check alone does not certify
   an independently assembled Docker image.

For GPL/LGPL software, commercial use is not itself prohibited. Requirements
depend on the actual component, linking/build choices, modifications and
distribution method. Do not infer that using an external FFmpeg process
automatically relicenses independent application code or its generated audio.
Conversely, do not treat an MIT root file as permission to omit corresponding
source when distributing GPL/LGPL binaries.

## Hosted-service integration

The reviewed Qwen models are commercially viable candidates at the license
level. A separate hosted service can call the engine over HTTP. That boundary
does not replace component-license obligations, and it does not automatically
make unrelated hosted-service source subject to the engine's source licenses.

Before using a saved voice commercially, retain its reference recording and
speaker permissions or document how the synthetic design reference was
generated. Commercial output and cross-engine cloning need their own quality,
provenance, consent and service-policy checks. An open model license is not a
license to somebody else's identity or copyrighted input.

## Repeatable checks

```bash
python scripts/check_licensing.py
python -m unittest discover -s tests -p test_licensing.py -v
python scripts/check_licensing.py --artifact dist/package.whl --artifact dist/package.tar.gz
```

Run these tooling checks with Python 3.13. The artifact names above are
placeholders for the actual build outputs. The checker verifies consolidated
license texts, notices, and package contents; it does not label a future image legally
approved or infer rights from an SPDX identifier alone.
