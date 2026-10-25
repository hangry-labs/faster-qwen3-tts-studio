# Qwen3-TTS SSML and SSML-H processor profile

The normative [SSML-H 1.0 specification](https://hangrylabs.app/ns/ssml-h/1.0)
is maintained in [ssml-h-spec](https://github.com/hangry-labs/ssml-h-spec).
This document describes this processor's supported subset. SSML-H is a Hangry
Labs extension to W3C SSML 1.1, not a W3C standard or a claim of full conformance.
The implementation uses `ssml-h-tools==0.3.1`, shared with VoxCPMTTS.

Choose `input_type="ssml"` or `"ssml-h"` explicitly on native API routes. Text
mode and OpenAI input never auto-detect markup. Compile with `/tts/plan` or
inspect `/tts/ssml/capabilities` without loading a model.

## Standard subset

Require one `<speak>` root, optionally using namespace
`http://www.w3.org/2001/10/synthesis` and version 1.0 or 1.1. Supported elements:
`metadata`, `p`, `s`, `token`, `w`, `voice`, `lang`, `break`, `prosody`, `sub`,
`say-as`. Unknown elements, attributes, namespaces, DTDs, entities and external
references fail before inference. `<audio>`, `<phoneme>` and lexicons are rejected.
Qwen consumes text tokens and does not expose a direct IPA input contract.

`<voice name="Ryan">` selects a native speaker or saved unique name/id. A voice
switch uses that voice's language unless an enclosing explicit `xml:lang`
overrides it. `<lang xml:lang="de-DE">` changes the language while retaining
the voice. Supported languages are Chinese, English, Japanese, Korean, German,
French, Russian, Portuguese, Spanish and Italian; corresponding language codes
and regional BCP-47 tags are accepted. Voice identity and language are distinct.

`<prosody rate="125%" pitch="+2st" volume="soft">` applies FFmpeg time stretch,
pitch shift and gain to that unit. Standard named presets and bounded numeric
forms are accepted by the shared parser. Nested rates/volumes multiply, pitches
add, and request speed multiplies the effective rate. Effective rate must be
0.25 to 4; shared bounds also enforce pitch and volume. Large transformations
can introduce artifacts. Complete-recording loudness normalization runs once
after assembly, never independently per turn.

`<break time="350ms"/>` and seconds are supported, as are standard strengths.
Only internal model padding is compacted. Adjacent speech gets a 120 ms handoff.
An explicit break replaces that gap, including `0ms`; outer recording edges
are preserved. Consecutive explicit breaks add. `<sub alias="spoken words">`
substitutes text; `say-as` supports characters, digits, cardinal and English
ordinal forms. Element tails retain their parent voice/language/prosody.

## SSML-H voices and direction

```xml
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:h="https://hangrylabs.app/ns/ssml-h/1.0" xml:lang="en-US">
  <metadata>
    <h:extensions version="1.0">
      <h:voice-definition name="Mara" scope="request" seed="1234">
        <h:description>A warm adult woman with a clear, gentle voice.</h:description>
        <h:sample xml:lang="en-US">Hello. My name is Mara. I enjoy telling stories.</h:sample>
      </h:voice-definition>
    </h:extensions>
  </metadata>
  <voice name="Mara" h:direction="Quietly, with cautious optimism.">We are ready.</voice>
  <break time="350ms"/>
  <voice name="Mara">Let us begin.</voice>
</speak>
```

VoiceDesign 1.7B creates each bootstrap reference. Base 0.6B clones that same
reference and exact known transcript for every matching turn. The reference is
request-owned; no ASR or network audio fetch is needed. Supported design
descriptors are gender, age, pitch, style, languages, accent, dialect and a
bounded free-form description. These become a voice description, with
probabilistic instruction following rather than guaranteed speaker traits.
Unsupported languages are rejected. If `h:sample` is omitted, use the deterministic
English passage advertised by the capabilities endpoint.

`scope="request"` keeps the voice in memory only. `scope="profile"` stages an
audio-backed profile and publishes it atomically with the other new profiles
after successful synthesis and encoding. A failed/cancelled stream publishes
none. `replace="true"` is required for an existing saved name; request definitions
cannot shadow saved or native voices. A single-turn Magic preview does not
commit document profiles. The explicit UI Save voice action saves the selected
generated take as a new clone reference.

`h:direction` works on `<voice>` and `<s>`, up to 240 characters. It directs
that turn without changing the reference identity. Base supports experimental
delivery instructions. Native directions require 1.7B CustomVoice; explicit
0.6B CustomVoice requests with direction fail before inference. Turn pitch
effects are separate from a definition's pitch descriptor.

## Limits and streaming

Source: 50000 characters, 300 elements, nesting 12, 200 semantic units, 12 voice
definitions, 500 bootstrap/description characters each, 10 seconds per break,
60 seconds of breaks total. The Qwen processor further limits requests to
64 compiled speech units, 6000 spoken characters and 300 seconds of output.
Automatic splitting uses at most 400 characters per call; disabling long-audio
protection raises the unit limit to 1000 without silently truncating text.

Full output, progressive audio, native SSE, Magic and plan inspection use the
same validation, routing and boundary rules. Markup streams codec audio within
speech units, with bounded internal-edge buffering and per-unit prosody filters.
Optional normalization processes the assembled stream once. One request-owned FIFO
lease serializes inference across models. System controls which defaults remain
resident; request-only weights release after the complete document. Crossing between
native speakers and clones loads any missing checkpoints; design references are
prepared together and reused across all matching turns. See [API](API.md).
