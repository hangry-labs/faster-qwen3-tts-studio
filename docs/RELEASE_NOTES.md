# Release notes

## v1.0-snapshot

The first Hangry Labs Studio development version. Python distributions use the
PEP 440 version `1.0.dev0`. This snapshot name does not create a stable release
or change the rolling Docker image tags.

- Maintain Qwen inference, compatibility changes and accelerated generation
  locally under `src/`, with provenance for all three upstream sources.
- Package the Studio for NVIDIA GPUs with Python 3.13 and local model caches.
- Provide voice design, saved-voice cloning with experimental delivery direction,
  built-in speakers, OpenAI-compatible speech and native speech APIs.
- Support Text, standard SSML, SSML-H and the Magic dialogue editor, including
  per-turn takes, retained takes, designed characters and saved workspaces.
- Isolate Text and SSML drafts when switching input modes. Import edited SSML-H
  into Magic only after validation, preserving the active draft on errors.
- Align Generate with the compact VoxCPMTTS layout, generation menus, joined
  Generate/Stream control, progress display, waveform players and finishing UI.
- Assemble completed Magic takes automatically after turn edits. Save settings,
  original output and processed previews with dialogue workspaces.
- Track progress per request. Preview MP3 streams progressively and retain the
  same recording for replay, download and finishing. Stream mode uses MP3;
  Generate mode uses the selected output format.
- Add bounded FFmpeg noise cleanup, EQ, compression, loudness normalization and
  optional pitch/speed shaping, with separate original and processed previews.
- Protect audio replacement from stale loads clearing newer recordings.

Native speaker direction requires the 1.7B CustomVoice model. Base delivery
direction remains experimental. Finishing uses FFmpeg; Signalsmith processing
and VoxCPM-specific model controls are not offered by this engine. Word timing
and subtitle export are not available. See [API capabilities](API.md) for the
supported input semantics and limits.
