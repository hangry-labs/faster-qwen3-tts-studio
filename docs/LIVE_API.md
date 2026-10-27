# Live speech API

Send text as an LLM produces it and receive audio from the same ongoing generation.
Connect to **`ws://localhost:7860/tts/live`**, using the same port as the Studio.
Use `wss://` when your server is behind HTTPS. Each connection handles one utterance.

## Try it

Save a reference voice in the Studio's Voices tab, including its exact transcript.
The existing `POST /tts/voice-profiles` upload API also accepts `reference_audio`
and `ref_text`; see [the speech API guide](API.md). From a repository checkout,
select its ID or unique name:

```bash
python -m pip install websockets
python examples/live_speech.py --voice "My saved voice" --text "Hello. This is a live speech request." --output speech.wav
```

The [Python client](../examples/live_speech.py) accepts an async iterable of text
fragments through `speak()`. Connect your LLM's text deltas to that iterable.
The CLI also reads text from standard input until EOF when `--text` is omitted.
It writes arriving audio into a WAV file; an application can instead send the
PCM chunks directly to its playback buffer.

## Reference modes

Both modes require `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, which is also selected when
`model` is omitted. The live endpoint rejects 0.6B models before queueing or loading
weights because their delivery was less consistent with streamed text input.
The complete-text HTTP APIs and Studio still support 0.6B generation.
For warm response latency, keep the selected Base model resident in System settings.
The live route honors that policy; it does not pin additional weights automatically.

| Setting | Conditioning |
|---|---|
| `xvec_only: false` (default) | Full-reference ICL: voice embedding, reference audio codes and matching transcript. |
| `xvec_only: true` | Speaker embedding only. A reference transcript is not required. |

ICL uses the transcript saved with the voice. Supply `ref_text` in `start` to
override it for this utterance. This is the transcript of the **reference
recording**, separate from the new text you send to be spoken. The voice library
is not modified. Reference data is resolved once, rather than sent per fragment.

Full-reference ICL needs an opening text buffer determined by the reference.
The `ready` event reports `initial_text_tokens`. Speech begins once enough stable
tokens are available, or once `finish` supplies the end of a shorter input.
Speaker-only cloning needs less opening text. The service does not switch modes
automatically.

## Messages

First send a JSON text frame:

```json
{"type":"start","voice":"VOICE_ID","model":"Qwen/Qwen3-TTS-12Hz-1.7B-Base","xvec_only":false,"seed":4210}
```

After `accepted`, forward text fragments and signal the end of the text:

```jsonl
{"type":"text","text":"Hello. "}
{"type":"text","text":"It is good to hear from you."}
{"type":"finish"}
```

Text can arrive while the request is queued or loading. You do not need to wait
for `ready` to send it. An optional `text` field in `start` supplies an initial
fragment. Send `{"type":"cancel"}` or close the connection to cancel.

The server returns JSON control frames and binary audio frames:

| Event | Meaning |
|---|---|
| `accepted` | Valid request, queue capacity reserved. Includes model, seed, resolved voice ID and audio format. |
| `queued` | FIFO inference queue position. |
| `loading` | Requested weights are loading, if needed. |
| `ready` | Reference prepared. Includes cloning mode and required opening token count. |
| Binary frame | Headerless signed 16-bit little-endian PCM, 24,000 Hz, mono. |
| `done` | Successful completion, including duration, samples, input wait and request timing metrics. |
| `cancelled` | Cancellation acknowledged. |
| `error` | Request failed or hit a generation limit. Includes `code` and `message`. |

Keep receiving after `finish`: it ends the text input, while speech generation
continues. Treat `done` as success; receiving some audio or a closed socket alone
does not establish that the utterance completed.

### Start options

`language`, `instruct`, `temperature`, `top_k`, `repetition_penalty`, `seed`,
`max_new_tokens`, `chunk_size` and `decoder_context_frames` use the existing Clone
generation controls. Settings remain fixed throughout the utterance.

- `max_new_tokens`: 24..600, default 600 codec frames, approximately 48 seconds
  of generated audio at the maximum. A budget stop returns `error`, not `done`.
- `chunk_size`: 1..64, default 8. Controls output audio packet size.
- `decoder_context_frames`: 1..200, default 25.
- `input_timeout_s`: 1..60 seconds, default 15. Applies while text remains open;
  send `finish` when there is no more text.

This route accepts plain text and PCM output. Complete-text HTTP endpoints remain
available for SSML, SSML-H, Magic and encoded audio formats. The native WebSocket
protocol is an extension, separate from the OpenAI-compatible HTTP speech route.

## Limits and scheduling

Discovery at `GET /studio/capabilities` includes `live_speech` with protocol and
resource limits. An utterance accepts up to 4,000 characters and 1,500 input tokens;
JSON frames must fit within 32 KiB. The active utterance has a 120-second wall time
limit. Connections have an overall 180-second limit including queue and load
time. A client that stops accepting output is disconnected after a bounded wait.

Live synthesis shares the existing bounded FIFO inference queue with HTTP requests.
One active utterance owns the inference state until completion or cleanup,
including waits for text. An idle connection before `start` reserves no queue slot
and has a 10-second start deadline. Disconnects and cancellations release their
admission and model lease; resident model settings remain under operator control.

Use a playback buffer. Slow or paused text delivery can create audible gaps even
when the generated samples are unchanged. Reconnect for the next utterance;
long responses should be divided into appropriately sized utterances.

Use reference voices you have permission to use. This endpoint follows the access
policy of the native `/tts` APIs; the optional key for `/v1` routes does not protect
it. See [deployment and access guidance](../README.md#docker-reference).
