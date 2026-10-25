# MCP speech tools

Studio serves Streamable HTTP MCP on the same port as its UI/API:

| Endpoint | Tools |
| --- | --- |
| `/mcp/` | Health/build identity, languages, saved/built-in voices, speech inspection and simple MP3 speech |
| `/mcp/advanced/` | All compact tools plus full Qwen generation controls, reference transcription, voice creation and deletion |

Both endpoints are disabled by default. Enable the required endpoint in **System →
MCP access**, save, then connect your client to `http://localhost:7860/mcp/` or
`http://localhost:7860/mcp/advanced/`. The switches are independent and persist in
the product volume. When `QWEN_STUDIO_API_KEY` is configured, send
`Authorization: Bearer YOUR_KEY` to either endpoint.

For another machine or a reverse proxy, set `QWEN_STUDIO_MCP_BASE_URL` to the
HTTP(S) origin clients can reach, such as `https://speech.example.com`. This
controls returned audio links and permits that MCP host. Add other permitted
authorities with `QWEN_STUDIO_MCP_ALLOWED_HOSTS` and browser origins with
`QWEN_STUDIO_MCP_ALLOWED_ORIGINS`, both comma separated. Host/origin validation
remains enabled. The System panel displays the configured download origin.

## Tools

`talk_simple` accepts exact `text`, optional `language` (default `Auto`),
`voice_id` (default `auto`) and `ttl_seconds` (default 3600). Auto selects Qwen's
built-in Ryan speaker using the configured CustomVoice model. A saved id selects
Base cloning. Simple generation uses seed 42 and returns MP3.

```json
{"text":"Good morning from the garden.","language":"English","voice_id":"auto","ttl_seconds":300}
```

`talk_advanced` accepts a `request` object with the same fields as native
`POST /tts/generate`, an optional `reference_audio_location`, and a link lifetime.
It supports all three Qwen model families, exact model selection, text/SSML/SSML-H,
delivery direction, sampling/seed controls, protected long text and all native
output formats. It returns the completed recording as a temporary link.

```json
{"request":{"text":"A quiet morning.","mode":"design","instruct":"A warm adult narrator with a clear conversational voice.","language":"English","seed":42,"output_format":"wav"},"ttl_seconds":300}
```

| Tool | Purpose |
| --- | --- |
| `get_health` | Current runtime, model catalog and build identity |
| `find_languages` | Search actual supported Qwen languages |
| `get_saved_voices_catalog` | Exact saved ids, metadata and built-in speaker names |
| `inspect_speech` | Validate text or markup without inference |
| `talk_simple` | Plain-text MP3 speech using Ryan or a saved id |
| `talk_advanced` | Full native speech request and optional reference location |
| `transcribe_reference` | Use the operator-configured ASR service |
| `create_cloned_voice_profile` | Explicitly save a permitted reference, transcript and metadata |
| `create_designed_voice_profile` | Generate and explicitly save a described voice and its recipe |
| `delete_saved_voice` | Remove a saved profile and its assets |

Profile mutation tools declare destructive/persistent effects. Existing names
require `replace=true`; replacements retain the saved id. Tools use the same
inference queue, checkpoint defaults, validation and library as the UI/API.
An overloaded queue produces an actionable tool error; cancellation stops its
request. Tool results contain links and metadata, never inline audio/base64.

## Audio links and persistence

Generated audio links are bearer capabilities: anyone holding a link can fetch
it until expiry. The download route does not require the MCP bearer key. Lifetimes
range from 60 seconds to 24 hours. Files survive container restart in
`/app/persistent/studio/mcp-output`, expire on access and are cleaned periodically.
Temporary storage is bounded to 512 files and 512 MiB; a full store rejects new
links rather than deleting recordings whose links are still valid.

Profile creation remains explicit. SSML-H `scope="profile"` also explicitly
requests persistence. If speech creates profiles and temporary-link storage then
fails, the tool error reports those already-created ids; it does not silently
delete saved voices. Disabling MCP prevents new tool requests while existing
download links retain their original expiry.

## Reference locations

Advanced MCP accepts relative or absolute container paths within
`/app/persistent/studio/mcp-input`, or another directory selected with
`QWEN_STUDIO_MCP_INPUT_DIR`. Parent traversal and symlink escape are rejected.
Mount or copy permitted audio into that directory; host paths outside it are
not readable through these tools.

HTTP(S) references have a 10 MB limit, 30-second total download deadline and at
most three redirects. Each destination is validated; DNS results are pinned for
the connection while preserving TLS hostname checks. Link-local, multicast,
reserved and unspecified addresses are rejected. Public and LAN hosts are
available by default; restrict them with `QWEN_STUDIO_AUDIO_URL_ALLOWED_HOSTS`,
using comma-separated hostnames, `host:port`, `*.example.com` or `*`. An empty list
disables URL inputs. Embedded credentials and other URL schemes are rejected.

Decoded reference audio is bounded to two minutes. Transcription sends audio
to the ASR service the operator configured; Studio does not load a local ASR
model. Only use recordings and speakers you are authorized to process or clone.

The service uses the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
with stateless Streamable HTTP transport. Bidirectional live-text speech and
legacy SSE transport endpoints are not provided.
