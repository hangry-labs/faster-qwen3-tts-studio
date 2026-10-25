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

Core dependencies and the Python base digest are pinned, but apt and the
transitive Python tree are not a complete artifact lock. Review the exact
distributed payload and its original terms. See
[container builds](RELEASING.md) and [Third-Party Notices](../THIRD_PARTY_NOTICES.md).

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
