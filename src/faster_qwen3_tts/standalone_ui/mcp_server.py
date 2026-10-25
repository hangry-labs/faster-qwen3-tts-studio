"""Opt-in MCP over the same Qwen API, queue and voice library as the browser.

Transport and capability-link patterns adapted from Apache-2.0 VoxCPMTTS; see NOTICE.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import hmac
import json
import os
import re
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException
from fastapi.responses import FileResponse, JSONResponse
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from .artifacts import ArtifactExpiredError, ArtifactNotFoundError, ArtifactStore
from .audio import FORMATS
from .build_info import build_identity
from .runtime import LANGUAGES, SPEAKERS
from .speech import SpeechRequest


class SpeechLink(BaseModel):
    download_url: str
    expires_at: str
    ttl_seconds: int
    format: str
    mime_type: str
    size_bytes: int
    duration_seconds: float
    sample_rate: int
    seed: int
    voice_mode: str
    voice: str
    language: str
    created_profiles: list[str]


class EndpointSlot:
    def __init__(self, enabled):
        self.enabled, self.app = enabled, None

    async def __call__(self, scope, receive, send):
        if not self.enabled():
            return await JSONResponse({'error': {'message': 'Enable this MCP endpoint in System before reconnecting.'}},
                                      status_code=403)(scope, receive, send)
        key = os.getenv('QWEN_STUDIO_API_KEY', '').strip()
        headers = dict(scope.get('headers', []))
        scheme, _, provided = headers.get(b'authorization', b'').decode('latin1').partition(' ')
        if key and (scheme.lower() != 'bearer' or not hmac.compare_digest(provided.encode(), key.encode())):
            return await JSONResponse({'error': {'message': 'A valid API bearer key is required.'}}, status_code=401,
                                      headers={'WWW-Authenticate': 'Bearer'})(scope, receive, send)
        if self.app is None:
            return await JSONResponse({'error': {'message': 'MCP is starting. Reconnect shortly.'}}, status_code=503)(scope, receive, send)
        await self.app(scope, receive, send)


class LocalAPI:
    def __init__(self, app):
        self.app = app

    async def request(self, method, path, **kwargs):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),
                                     base_url='http://127.0.0.1', timeout=None) as client:
            response = await client.request(method, path, **kwargs)
        if not response.is_success:
            try:
                data = response.json()
                message = data.get('detail') or data.get('error', {}).get('message')
            except ValueError:
                message = None
            raise ToolError(f'{message or "The request failed."} (HTTP {response.status_code})')
        return response


def create_mcp_server(app, *, store, base_url, advanced):
    tier = 'advanced' if advanced else 'compact'
    api = LocalAPI(app)
    server = MCPServer('qwen3-tts-' + tier, title='Qwen3-TTS Studio ' + tier.title(),
        version=build_identity()['version'],
        instructions='Use talk_simple for ordinary speech, passing the exact text verbatim. '
        'voice_id=auto uses the Ryan built-in voice; saved ids use Base cloning. '
        'Results are expiring download links, never inline audio. '
        'Persistent voice mutations require a user request. Use advanced tools for Qwen controls, design, references and SSML-H.')
    read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    generate = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
    external = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True)
    mutate = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=True)

    async def read_reference(location):
        try:
            return await app.state.references.read(location)
        except (ValueError, OSError) as exc:
            raise ToolError(str(exc)) from exc

    async def generate_link(request, ttl_seconds, reference_audio_location=''):
        if not 60 <= ttl_seconds <= 86400:
            raise ToolError('Choose a link lifetime from 60 to 86400 seconds.')
        payload = request.model_dump()
        if reference_audio_location:
            if request.ref_audio or request.voice_profile:
                raise ToolError('Choose one saved voice or reference location.')
            upload = await read_reference(reference_audio_location)
            try:
                response = await api.request('POST', '/tts/generate-upload', data={'payload': json.dumps(payload)},
                    files={'reference_audio': (upload.filename or 'reference.wav', await upload.read(), 'application/octet-stream')})
            finally:
                await upload.close()
        else:
            response = await api.request('POST', '/tts/generate', json=payload)
        metrics = json.loads(response.headers.get('X-Qwen-Metrics', '{}'))
        committed = json.loads(response.headers.get('X-Qwen-Committed-Profiles', '{}'))
        mode = 'reference' if reference_audio_location or request.ref_audio else 'saved' if request.voice_profile else request.mode or 'custom'
        try:
            artifact = await asyncio.to_thread(store.create, response.content,
                extension=request.output_format, ttl_seconds=ttl_seconds, format=request.output_format,
                mime_type=FORMATS[request.output_format][0], duration_seconds=metrics.get('duration_s', 0),
                sample_rate=int(response.headers['X-Qwen-Sample-Rate']), seed=int(response.headers['X-Qwen-Seed']),
                voice_mode=mode, voice=request.voice_profile or request.voice, language=request.language,
                created_profiles=list(committed.values()))
        except (ValueError, OSError) as exc:
            detail = f' Saved profiles were already created: {list(committed.values())}.' if committed else ''
            raise ToolError(str(exc) + detail) from exc
        return SpeechLink(**artifact.public_metadata(base_url + '/tts/artifacts/' + artifact.token))

    @server.tool(annotations=read, structured_output=True)
    async def get_health() -> dict[str, Any]:
        """Read readiness, Qwen model families, build identity and MCP connection details."""
        return {'product': 'Faster Qwen3-TTS Studio', **build_identity(),
                'runtime': app.state.engine.status(), 'models': (await api.request('GET', '/studio/capabilities')).json()['models'],
                'mcp': {'tier': tier, 'endpoint': '/mcp/advanced/' if advanced else '/mcp/',
                        'download_base_url': base_url, 'returns_raw_audio': False}}

    @server.tool(annotations=read, structured_output=True)
    async def find_languages(query: Annotated[str, Field(max_length=100)] = '',
                             limit: Annotated[int, Field(ge=1, le=50)] = 10) -> dict[str, Any]:
        """Find the actual Qwen supported languages; Auto enables model detection."""
        matches = [name for name in LANGUAGES if query.casefold() in name.casefold()][:limit]
        return {'count': len(matches), 'languages': matches}

    @server.tool(annotations=read, structured_output=True)
    async def get_saved_voices_catalog() -> dict[str, Any]:
        """List exact saved ids and Qwen built-in speaker names without generating audio."""
        result = (await api.request('GET', '/tts/voice-profiles')).json()
        return {'count': result['count'], 'voices': result['data'], 'built_in_voices': SPEAKERS}

    @server.tool(annotations=read, structured_output=True)
    async def inspect_speech(text: Annotated[str, Field(min_length=1, max_length=50000)],
                             input_type: str = 'text', language: str = 'Auto', voice_id: str = 'auto') -> dict[str, Any]:
        """Validate exact text or SSML/SSML-H and inspect its speech plan without inference."""
        return (await api.request('POST', '/tts/plan', json={'text': text, 'input_type': input_type,
            'language': 'Auto' if language.casefold() == 'auto' else language,
            'voice_profile': None if voice_id == 'auto' else voice_id})).json()

    @server.tool(annotations=generate, structured_output=True)
    async def talk_simple(text: Annotated[str, Field(min_length=1, max_length=50000,
                         description='Exact user speech text, verbatim; do not paraphrase.')],
                          language: str = 'Auto', voice_id: str = 'auto',
                          ttl_seconds: Annotated[int, Field(ge=60, le=86400)] = 3600) -> SpeechLink:
        """Generate plain-text MP3 using Ryan or a saved voice; return a temporary link."""
        return await generate_link(SpeechRequest(text=text, output_format='mp3', seed=42,
            language='Auto' if language.casefold() == 'auto' else language,
            voice_profile=None if voice_id == 'auto' else voice_id), ttl_seconds)

    if advanced:
        @server.tool(annotations=external, structured_output=True)
        async def talk_advanced(request: SpeechRequest,
                                reference_audio_location: Annotated[str, Field(max_length=2048)] = '',
                                ttl_seconds: Annotated[int, Field(ge=60, le=86400)] = 3600) -> SpeechLink:
            """Generate with actual Qwen model/sampling/direction/SSML-H controls and optional bounded local/HTTP reference."""
            return await generate_link(request, ttl_seconds, reference_audio_location)

        @server.tool(annotations=external, structured_output=True)
        async def transcribe_reference(audio_location: Annotated[str, Field(min_length=1, max_length=2048)]) -> dict[str, Any]:
            """Transcribe permitted local/HTTP reference audio through the operator's configured ASR service."""
            upload = await read_reference(audio_location)
            try:
                return (await api.request('POST', '/tts/transcribe-upload', files={
                    'reference_audio': (upload.filename or 'reference.wav', await upload.read(), 'application/octet-stream')})).json()
            finally:
                await upload.close()

        @server.tool(annotations=mutate, structured_output=True)
        async def create_cloned_voice_profile(name: Annotated[str, Field(min_length=1, max_length=80)],
            audio_location: Annotated[str, Field(min_length=1, max_length=2048)],
            reference_text: Annotated[str, Field(max_length=4000)] = '', language: str = 'English',
            description: Annotated[str, Field(max_length=1500)] = '', tags: list[str] | None = None,
            replace: bool = False) -> dict[str, Any]:
            """Explicitly save a permitted reference in the persistent library. Replacement requires replace=true."""
            upload = await read_reference(audio_location)
            try:
                return (await api.request('POST', '/tts/voice-profiles', data={'name': name, 'ref_text': reference_text,
                    'language': language, 'description': description, 'tags': json.dumps(tags or []), 'replace': str(replace).lower(),
                    'profile_type': 'reference', 'recipe': json.dumps({'version': 1, 'workflow': 'reference', 'settings': {'language': language}})},
                    files={'reference_audio': (upload.filename or 'reference.wav', await upload.read(), 'application/octet-stream')})).json()
            finally:
                await upload.close()

        @server.tool(annotations=mutate, structured_output=True)
        async def create_designed_voice_profile(name: Annotated[str, Field(min_length=1, max_length=80)],
            description: Annotated[str, Field(min_length=1, max_length=1500)],
            sample_text: Annotated[str, Field(min_length=1, max_length=1000)], language: str = 'English',
            seed: Annotated[int, Field(ge=0, le=2**32-1)] = 42, replace: bool = False) -> dict[str, Any]:
            """Design and explicitly save an audio-backed reusable voice. Uses the configured VoiceDesign checkpoint."""
            request = SpeechRequest(text=sample_text, mode='design', model=app.state.engine.workflow_models['design'], instruct=description,
                                    language=language, seed=seed, output_format='wav')
            response = await api.request('POST', '/tts/generate', json=request.model_dump())
            settings = request.model_dump()
            return (await api.request('POST', '/tts/voice-profiles', data={'name': name, 'ref_text': sample_text,
                'language': language, 'description': description, 'replace': str(replace).lower(), 'profile_type': 'design',
                'recipe': json.dumps({'version': 1, 'workflow': 'design', 'selected_version': 'original', 'settings': settings})},
                files={'reference_audio': ('design.wav', response.content, 'audio/wav')})).json()

        @server.tool(annotations=mutate, structured_output=True)
        async def delete_saved_voice(voice_id: str) -> dict[str, Any]:
            """Delete a saved voice and its persistent assets only when the user explicitly requests removal."""
            if not re.fullmatch(r'[a-f0-9]{32}', voice_id):
                raise ToolError('Use the exact saved voice id from get_saved_voices_catalog.')
            return (await api.request('DELETE', '/tts/voice-profiles/' + voice_id)).json()

    return server


def attach_mcp(app, *, data: Path, settings):
    base = os.getenv('QWEN_STUDIO_MCP_BASE_URL', 'http://localhost:7860').strip().rstrip('/')
    parsed = urlsplit(base)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
        raise ValueError('QWEN_STUDIO_MCP_BASE_URL must be an HTTP(S) origin without credentials or a path.')
    store = ArtifactStore(data / 'mcp-output')
    compact_slot = EndpointSlot(lambda: settings.get('mcp_enabled', False))
    advanced_slot = EndpointSlot(lambda: settings.get('mcp_advanced_enabled', False))
    security = TransportSecuritySettings(enable_dns_rebinding_protection=True,
        allowed_hosts=list(dict.fromkeys(['127.0.0.1', '127.0.0.1:*', 'localhost', 'localhost:*', '[::1]', '[::1]:*',
            'host.docker.internal', 'host.docker.internal:*', parsed.netloc,
            *filter(None, os.getenv('QWEN_STUDIO_MCP_ALLOWED_HOSTS', '').split(','))])),
        allowed_origins=list(filter(None, os.getenv('QWEN_STUDIO_MCP_ALLOWED_ORIGINS',
            'http://localhost:*,http://127.0.0.1:*,http://host.docker.internal:*').split(','))))
    original = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(instance):
        # Each application lifespan gets fresh SDK managers; they are single-use.
        compact = create_mcp_server(app, store=store, base_url=base, advanced=False)
        advanced = create_mcp_server(app, store=store, base_url=base, advanced=True)
        for slot, server in [(compact_slot, compact), (advanced_slot, advanced)]:
            slot.app = server.streamable_http_app(streamable_http_path='/', json_response=True,
                stateless_http=True, max_request_body_size=1024 * 1024, transport_security=security)
        app.state.mcp_compact_server, app.state.mcp_advanced_server = compact, advanced
        await asyncio.to_thread(store.cleanup_expired)

        async def cleanup():
            while True:
                await asyncio.sleep(60)
                await asyncio.to_thread(store.cleanup_expired)

        task = asyncio.create_task(cleanup())
        try:
            async with original(instance), compact.session_manager.run(), advanced.session_manager.run():
                yield
        finally:
            compact_slot.app = advanced_slot.app = None
            task.cancel(); await asyncio.gather(task, return_exceptions=True)

    app.router.lifespan_context = lifespan
    app.state.artifacts = store
    app.mount('/mcp/advanced', advanced_slot, name='mcp-advanced')
    app.mount('/mcp', compact_slot, name='mcp-compact')

    @app.get('/system/mcp')
    def status():
        return {'enabled': settings['mcp_enabled'], 'advanced_enabled': settings['mcp_advanced_enabled'],
                'compact_path': '/mcp/', 'advanced_path': '/mcp/advanced/', 'download_base_url': base,
                'url_reference_available': app.state.references.fetcher.enabled, 'ttl_min': 60, 'ttl_max': 86400}

    @app.api_route('/tts/artifacts/{token}', methods=['GET', 'HEAD'], include_in_schema=False)
    async def download(token: str):
        try:
            artifact, path = await asyncio.to_thread(store.resolve, token)
        except ArtifactExpiredError as exc:
            raise HTTPException(410, str(exc)) from exc
        except ArtifactNotFoundError as exc:
            raise HTTPException(404, str(exc)) from exc
        return FileResponse(path, media_type=artifact.mime_type, filename=artifact.filename,
                            headers={'Cache-Control': 'private, no-store'})
