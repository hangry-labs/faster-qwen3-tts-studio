# Faster Qwen3-TTS Studio examples

Open **Examples** in the Studio, or visit `http://localhost:7860/examples/`.
The same static page can be hosted on GitHub Pages or opened directly from
`index.html`. Its scripts, styles, artwork and audio work without a CDN.

From a repository checkout, `task examples` previews it at
`http://127.0.0.1:9000/` without loading models.

The gallery includes ten supported languages, ten designed voices per language,
three introduction variants, and a shared English-reference clone demonstration.
The featured SSML-H scene combines three designed characters with explicit pauses.
Choose a language to hear an introduction; click a card to play or pause it.
Each card exposes its voice recipe, lossless reference and audio downloads.

## Voice and text definitions

`definitions.json` is the editable source. Each voice includes its description,
reference text, language and design seed. Each language defines its sample texts,
voice selection and speech seeds. The two model identities and synthesis settings
are explicit. Every voice reference is synthetic, generated with 1.7B VoiceDesign.
The variety and introduction samples use references designed in the matching
language, then speak new text with 1.7B Base ICL and the exact reference transcript.
Each language also has a separate clone demo from the same English reference;
cross-language pronunciation and accent may differ. These are ten voice design
profiles, with distinct native-language references, rather than an identity
guarantee across languages. No third-party speaker recordings are used.

`assets/manifest.json` records the actual requests, pinned model revisions,
reference and output checksums, durations and file sizes. `voices.js` embeds that
manifest so the page also works through `file://` without fetching JSON.
Reference FLAC files retain the exact PCM used for cloning; listening clips use
Ogg Opus at 64 kbps VBR, encoded directly from generated PCM. Opus is lossy;
lossless references remain available for cloning and comparison. The encoding
settings are included in each clip's recipe and cache fingerprint.
Playback works in current Chromium/Firefox and Safari 18.4+ on supported Apple
systems ([WebKit support details](https://webkit.org/blog/16574/webkit-features-in-safari-18-4/)).
These are listening examples, not performance benchmarks or guarantees of
voice identity or pronunciation in every language.

## Regenerate

Start the Studio with its model cache available, then run:
Select 1.7B VoiceDesign and 1.7B Base as the Design and Clone defaults in System
for the SSML-H featured scene. The generator checks these defaults without
changing them; ordinary voice clips explicitly select their models per request.

```powershell
task examples-generate
```

The task uses the development image for FFmpeg and makes HTTP requests to the
running Studio. It does not change settings or add voices to your library.
Completed clips are reused only when the request, model revision, reference and
output checksums match. Partial runs can be resumed with the same command.

For separate model phases:

```powershell
task examples-generate -- --phase design
task examples-generate -- --phase speech
task examples-generate -- --phase featured
```

Keep VoiceDesign resident for the first phase and Base resident for the second
when memory permits. This is an operator choice; the script does not adjust
residency. The Python entry point is `python -m scripts.generate_gallery` and
requires FFmpeg on `PATH` if used outside the task's container.

The gallery and its media ship with the Docker images and repository. Python
wheel/source distributions retain the lightweight live API client rather than
bundling the listening collection. For that client, see [the live API guide](../docs/LIVE_API.md).
