# Third-party notices

Faster Qwen3-TTS Studio combines independently licensed code, model assets,
Python packages, native libraries, and operating-system components. The root
MIT license does not cover the complete combined runtime.

This inventory was reviewed on 2026-10-23. See [the licensing audit](docs/LICENSING.md)
for the commercial-use decisions, scope, findings, and remaining image-release
requirements. Original license texts and notices take precedence over summaries.

## Source and adaptations

| Component | License | Attribution and source |
| --- | --- | --- |
| Faster Qwen3-TTS wrapper | MIT | Copyright 2026 Andres Marafioti; [upstream](https://github.com/andimarafioti/faster-qwen3-tts); text in [LICENSE](LICENSE) |
| Qwen3-TTS input/model integration | Apache-2.0 | Copyright 2026 the Alibaba Qwen team; applicable upstream files also name Alibaba Group and HuggingFace Inc.; [source](https://github.com/QwenLM/Qwen3-TTS/tree/022e286b98fbec7e1e916cb940cdf532cd9f488e) |
| Qwen3-TTS-streaming adaptations | Apache-2.0 | Qwen authors, dffdeeq, and contributors; [reviewed source](https://github.com/dffdeeq/Qwen3-TTS-streaming/tree/13ef823ffe76aec4ac7e35d3fec28ecfc8d7427a) |
| qwen-tts-hf 0.1.1.post1 | Apache-2.0 | Qwen authors; Transformers 5 compatibility distribution maintained by Andres Marafioti; [publishing source](https://github.com/andimarafioti/Qwen3-TTS/tree/af457d954d8ce797603c6f260c3f911a09b1d90a) |
| nano-qwen3tts-vllm, acknowledged inspiration | MIT | Copyright 2026 Thanh Sang; [source](https://github.com/tsdocode/nano-qwen3tts-vllm/tree/ea48202b8398128c6aa8109c3e0ceb1bfb2e7a6b) |

[NOTICE](NOTICE) identifies adaptations. Preserve the source copyright headers,
NOTICE, [Apache-2.0 text](#apache-20-license-text), and other applicable
license files when distributing source, Python packages, or images. Apache
attribution does not require turning the independent application into Apache-only
software, and an MIT label cannot remove the Apache obligations.

## Model weights and tokenizer

The five official `Qwen/Qwen3-TTS-12Hz-*` checkpoints used by the project and
`Qwen/Qwen3-TTS-Tokenizer-12Hz` declare **Apache-2.0** at the reviewed revisions.
This includes both Base sizes, both CustomVoice sizes, and 1.7B VoiceDesign.

- Publisher: the Qwen team, Alibaba.
- [Reviewed model IDs, immutable revisions, and upstream cards](docs/LICENSING.md#decisions-for-the-official-qwen-models).
- [License text](#apache-20-license-text).

No standalone LICENSE or NOTICE file was present in those model repositories at
the inspected revisions. The reviewed declarations are linked in the audit;
the Apache text is supplied below. Retain model cards and any license/NOTICE
files alongside models in a distributed image or cache. Preserve upstream notices if later
revisions introduce them. Do not infer permission for an unrelated Qwen model,
fine-tune, voice recording, or model-hosting asset from this review.

The 12 Hz speech tokenizer is Qwen's separately released codec. The Python code
uses Transformers Mimi architecture classes; this does not mean Kyutai/Moshi
model weights are downloaded or bundled by this project. Do not substitute a
different tokenizer checkpoint under the same licensing conclusion.

## Optional reference transcription

- **nano-parakeet 0.2.1 code:** MIT, Copyright 2026 Andrés Marafioti.
  [Upstream](https://github.com/andimarafioti/nano-parakeet/tree/26ee76064235b95b92782ddd4bbd05f6d99550ae),
  [MIT notice](#nano-parakeet-mit-notice).
  The inspected wheel omits its root license file. This bundle supplies the
  upstream notice instead of assuming wheel packaging is complete.
- **NVIDIA Parakeet TDT 0.6B v3 weights:** CC BY 4.0, NVIDIA.
  [Model](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/tree/541d1f99c6b0c3cd0b11a95167540bb8edefd82b),
  [license](https://creativecommons.org/licenses/by/4.0/), and linked model card.
  The nano-parakeet wheel also bundles a SentencePiece tokenizer extracted
  from the NVIDIA checkpoint. Keep the NVIDIA attribution with that tokenizer,
  not just with a separately downloaded weights file. Neither tokenizer nor
  weights are relicensed under nano-parakeet's MIT code license.
  All 8192 ordered vocabulary entries match the official pinned model's
  tokenizer JSON; [the audit](docs/LICENSING.md#optional-asr-has-an-independent-model-license)
  identifies the bundled artifact and the comparison's limits.
  This project has not modified the NVIDIA weights or tokenizer. If a release
  changes or converts them, identify those changes with the attribution.
- **SentencePiece code:** Apache-2.0, Google and contributors; preserve its
  installed notices in addition to the model-tokenizer attribution above.

CC BY 4.0 permits commercial use and redistribution with attribution, a license
link, retention of supplied notices, and identification of changes. It does
not license the user's original recording or grant personality/privacy rights.

## Python runtime and native payloads

Keep complete license, copyright, and bundled-component notices in the installed
distributions, normally under `site-packages/*.dist-info/licenses/` or the
package's own directory. Retain Python's own license as well. Preserve full
notices rather than relying only on the package metadata's SPDX label.

The audit inspected a licensing-only candidate, not a tested runtime or lockfile.
Its extracted dependency notices and source archives are not part of this
source distribution. Collect the actual release image's inventory with
`scripts/collect_runtime_licenses.py`; review missing notices and supply them
from the matching upstream before release. The nano-parakeet and experimental
native notices below supplement omissions in the inspected wheels.

Important components and obligations:

| Component | Terms to preserve or satisfy |
| --- | --- |
| PyTorch/TorchAudio, NumPy, SciPy, scikit-learn | BSD/permissive source plus bundled-component licenses; scientific wheels can contain GCC runtime libraries with runtime exceptions, OpenBLAS, LAPACK, and other notices |
| Transformers, Accelerate, Hub, Tokenizers, ONNX Runtime | Primarily Apache-2.0 or MIT; retain exact package and bundled third-party notices |
| FastAPI, Pydantic, Gradio, Uvicorn, HTTP libraries | Respective MIT/Apache/BSD terms; qwen-tts-hf pulls Gradio even though this project's UI is custom FastAPI |
| Librosa | ISC code; its transitive SoXR dependency has separate LGPL obligations |
| Python-SoXR and bundled libsoxr/PFFFT | LGPL-2.1-or-later and PFFFT's notice; preserve licenses, corresponding source, and a usable replacement/relinking route for the exact distributed native build |
| certifi, tqdm, and orjson's covered components | MPL-2.0 portions, alongside MIT/Apache alternatives or other covered portions as specified; retain notices and make corresponding covered source available |
| SoundFile and libsndfile | SoundFile is BSD; an installed or wheel-bundled libsndfile is independently LGPL-2.1-or-later; inspect the actual binary, codec libraries, and how it was built |
| Python sox package | BSD Python wrapper; does not relicense the separate SoX executable or libsox |
| pydub, sounddevice | Optional MIT helpers; FFmpeg and platform PortAudio binaries have independent terms |
| FlashAttention | Optional BSD-3-Clause component attempted by inherited setup scripts; review the selected wheel/source and bundled notices before shipping |

Source archives for a research candidate do not satisfy source obligations for
different versions, distribution patches, omitted build inputs, or other native
libraries. Supply the required corresponding source for the actual distributed
build using a delivery method permitted by each applicable license. Exact
release-image compliance remains a separate build qualification.

## Operating system, codecs, and NVIDIA

The inherited demo Dockerfile uses Ubuntu 24.04 with CUDA 12.8.1/cuDNN and
installs FFmpeg, SoX, libsndfile, Git, and dependencies through apt. That is a
mixed-license distribution, including GPL/LGPL components and NVIDIA terms.

- Retain `/usr/share/doc/*/copyright`, `/usr/share/common-licenses/`, Python's
  license, package notices, NVIDIA EULAs/notices, and exact binary/source
  package/version identities. Do not strip these to reduce image size.
- FFmpeg's license depends on its build configuration. An LGPL-only build,
  GPL-enabled Ubuntu build, and nonfree build have different redistribution
  consequences. Inspect `ffmpeg -version` and `ffmpeg -buildconf`; do not
  redistribute a nonfree build as if it were an ordinary GPL/LGPL build.
- Supply the exact required corresponding source and build/patch materials
  with a release, or use another license-compliant delivery mechanism. Merely
  linking to a floating upstream branch is not an exact source bundle.
- CUDA/cuDNN are not MIT/Apache software. Redistribute only permitted runtime
  components under the matching NVIDIA terms, keep their notices, and do not
  present the image as an unrestricted copy of the complete SDK.
- Codec patent, trademark, privacy, and personality rights are not granted
  by these software licenses. They need consideration for the actual service,
  jurisdictions, input audio, and output format.

Use [the runtime notice collector](scripts/collect_runtime_licenses.py) inside
the actual candidate image. Its output is evidence collection, not automatic
legal approval or a substitute for corresponding source.

## Experimental GGML path

The unsupported experimental extra is still present in source:

- qwentts-cpp-python 0.5.0: MIT, Andres Marafioti.
- Embedded qwentts.cpp revision `6fae92914045cd83364d2845ceaa0f7969727319`:
  MIT, the omnivoice.cpp authors as named in its original license.
- Embedded ggml revision `40e16e4a814f7fe851a0c486fb9e8c722e957830`:
  retain the ggml and bundled-component notices.
- cpp-httplib: retain its original MIT notice.
- [`Serveurperso/Qwen3-TTS-GGUF`](https://huggingface.co/Serveurperso/Qwen3-TTS-GGUF/tree/b7ee2e8c7459c3bea99da23e3d178125a7d1713c)
  declares Apache-2.0 at the reviewed revision. It is separate from the official
  Qwen checkpoints.

The inspected Linux CUDA wheel retained only the wrapper's MIT license, so
supplemental native notices are needed. Native build variants, CUDA runtime
contents, and converted-model provenance must be reviewed for an actual GGML
release. This audit does not qualify a GGML or Apple Silicon product. The
supported product direction is NVIDIA/Torch.

## Recordings and generated media

The inherited reference recordings and generated comparison WAV files lacked
an independently documented media grant and recording/speaker provenance.
They were removed from the current distributable tree. No finding of infringement
is asserted. No permission to reuse a recording or imitate its speaker is
inferred from the repository's MIT license.

Demo reference presets no longer fetch recordings from upstream. Supply your
own permitted reference audio and an accurate transcript for cloning. Existing
Git history and previous upstream releases have not been rewritten or cleared
by this cleanup. Do not represent historical audio assets as reviewed examples.

For newly generated audio, the reviewed Qwen licenses impose no separate
noncommercial or output-royalty term. That is not a warranty of copyright
ownership, uniqueness, consent, or freedom from third-party rights. Commercial
voice profiles and cloning references require their own documented provenance.

## Supplemental license texts

The texts below supply source and supplemental notices in one place. They do
not replace the notices carried by other installed or bundled components.

### nano-parakeet MIT notice

```text
MIT License

Copyright (c) 2026 Andrés Marafioti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### nano-qwen3tts-vllm MIT notice

```text
MIT License

Copyright (c) 2026 Thanh Sang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### qwentts-cpp-python MIT notice

```text
MIT License

Copyright (c) 2026 Andres Marafioti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### qwentts.cpp MIT notice

```text
MIT License

Copyright (c) 2023-2026 The omnivoice.cpp authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### ggml MIT notice

```text
MIT License

Copyright (c) 2023-2026 The ggml authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### cpp-httplib MIT notice

```text
The MIT License (MIT)

Copyright (c) 2017 yhirose

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Apache-2.0 license text

```text
Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2026 Alibaba Cloud

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
