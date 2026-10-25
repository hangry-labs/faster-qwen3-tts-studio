"""MCP catalog, actual HTTP transport, shared generation and temporary links."""
import asyncio
import json
import threading
from pathlib import Path
from urllib.parse import urlsplit

from fastapi.testclient import TestClient
from mcp.server.mcpserver.exceptions import ToolError
import pytest

from faster_qwen3_tts.standalone_ui.server import create_app
from faster_qwen3_tts.standalone_ui.runtime import StudioEngine
from test_speech_api import Engine, api
from test_voice_library import recording


def call(app, name, arguments=None, *, advanced=False):
    server = app.state.mcp_advanced_server if advanced else app.state.mcp_compact_server
    return asyncio.run(server.call_tool(name, arguments or {}))


def test_catalogs_expose_actual_qwen_controls(api):
    client, engine, service = api
    app = client.app
    compact = {tool.name: tool for tool in asyncio.run(app.state.mcp_compact_server.list_tools())}
    advanced = {tool.name: tool for tool in asyncio.run(app.state.mcp_advanced_server.list_tools())}
    assert set(compact) == {'get_health', 'find_languages', 'get_saved_voices_catalog', 'inspect_speech', 'talk_simple'}
    assert set(advanced) - set(compact) == {'talk_advanced', 'transcribe_reference', 'create_cloned_voice_profile',
                                         'create_designed_voice_profile', 'delete_saved_voice'}
    schema = advanced['talk_advanced'].input_schema
    speech = schema['$defs']['SpeechRequest']['properties']
    assert {'model', 'temperature', 'top_k', 'chunk_size', 'xvec_only', 'instruct', 'ref_text'} <= set(speech)
    assert 'cfg_value' not in speech and 'inference_timesteps' not in speech
    assert advanced['delete_saved_voice'].annotations.destructive_hint
    assert call(app, 'get_health').structured_content['runtime']['state'] == 'idle'
    assert not engine.requests


def test_simple_and_saved_speech_return_downloadable_capability_links(api):
    client, engine, _ = api
    result = call(client.app, 'talk_simple', {'text': 'The exact words.', 'ttl_seconds': 60})
    assert not result.is_error, result
    payload = result.structured_content
    assert not {'text', 'audio', 'audio_b64'} & payload.keys()
    path = urlsplit(payload['download_url']).path
    response = client.get(path)
    assert response.status_code == 200 and response.headers['content-type'] == 'audio/mpeg'
    assert len(response.content) == payload['size_bytes']
    assert client.head(path).content == b''
    token = path.rsplit('/', 1)[1]
    artifact, file = client.app.state.artifacts.resolve(token)
    with pytest.raises(FileNotFoundError):
        client.app.state.artifacts.resolve(token, now=artifact.expires_at)
    assert not file.exists() and client.get(path).status_code == 404
    assert engine.requests[0][0].text == 'The exact words.'


def test_advanced_reference_and_profile_creation_share_native_routes(api, tmp_path):
    client, engine, service = api
    app = client.app
    app.state.references.root.mkdir()
    (app.state.references.root / 'source.wav').write_bytes(recording())
    result = call(app, 'talk_advanced', {'request': {'text': 'New words.', 'mode': 'clone', 'ref_text': 'Original words.',
        'instruct': 'Quietly', 'temperature': .75}, 'reference_audio_location': 'source.wav'}, advanced=True)
    assert not result.is_error, result
    assert engine.requests[-1][0].mode == 'clone' and engine.requests[-1][0].instruct == 'Quietly'
    assert engine.requests[-1][1] is not None
    saved = call(app, 'create_cloned_voice_profile', {'name': 'Reference', 'audio_location': 'source.wav',
        'reference_text': 'Original words.', 'tags': ['warm']}, advanced=True)
    assert not saved.is_error, saved
    identity = saved.structured_content['id']
    cloned = call(app, 'talk_simple', {'text': 'Saved speech.', 'voice_id': identity})
    assert not cloned.is_error and engine.requests[-1][0].ref_text == 'Original words.'
    with pytest.raises(ToolError, match='Explicit replacement'):
        call(app, 'create_cloned_voice_profile', {'name': 'Reference', 'audio_location': 'source.wav'}, advanced=True)
    assert len(service.voices.list()) == 1
    designed = call(app, 'create_designed_voice_profile', {'name': 'Designed', 'description': 'A calm storyteller.',
        'sample_text': 'The morning garden.', 'seed': 91}, advanced=True)
    assert not designed.is_error, designed
    record = service.voices.resolve(designed.structured_content['id'])
    assert record['recipe']['settings']['seed'] == 91 and record['profile_type'] == 'design'
    assert not call(app, 'delete_saved_voice', {'voice_id': identity}, advanced=True).is_error
    assert len(service.voices.list()) == 1


def test_http_transport_gates_key_and_repeat_lifespan(tmp_path, monkeypatch):
    monkeypatch.setenv('QWEN_STUDIO_API_KEY', 'private-test-key')
    app = create_app(Engine(), tmp_path)
    init = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
        'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1'}}}
    headers = {'Accept': 'application/json, text/event-stream', 'MCP-Protocol-Version': '2025-06-18'}
    for _ in range(2):
        with TestClient(app, base_url='http://localhost') as client:
            if not client.get('/system/settings').json()['mcp_enabled']:
                assert client.post('/mcp/', json=init, headers=headers).status_code == 403
            client.put('/system/settings', json={'mcp_enabled': True})
            assert client.post('/mcp/', json=init, headers=headers).status_code == 401
            authorized = {**headers, 'Authorization': 'Bearer private-test-key'}
            response = client.post('/mcp/', json=init, headers=authorized)
            assert response.status_code == 200, response.text
            assert response.json()['result']['serverInfo']['name'] == 'qwen3-tts-compact'
            assert client.post('/mcp/advanced/', json=init, headers=authorized).status_code == 403
            response = client.post('/mcp/', json={'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'}, headers=authorized)
            assert response.status_code == 200 and len(response.json()['result']['tools']) == 5
            client.put('/system/settings', json={'mcp_advanced_enabled': True})
            assert client.post('/mcp/advanced/', json=init, headers=authorized).status_code == 200
            client.put('/system/settings', json={'mcp_advanced_enabled': False})
    with TestClient(create_app(Engine(), tmp_path), base_url='http://localhost') as client:
        assert client.get('/system/settings').json()['mcp_enabled'] is True
        assert client.get('/system/settings').json()['mcp_advanced_enabled'] is False
        assert client.put('/system/settings', json={'mcp_enabled': 'true'}).status_code == 422


def test_native_local_references_reject_url_traversal_and_ambiguity(api):
    client, engine, _ = api
    root = client.app.state.references.root
    root.mkdir(); (root / 'source.wav').write_bytes(recording())
    payload = {'text': 'New words.', 'mode': 'clone', 'ref_audio': 'source.wav', 'ref_text': 'Original words.'}
    assert client.post('/tts/plan', json=payload).status_code == 200
    assert not engine.requests
    assert client.post('/tts/generate', json=payload).status_code == 200
    for location in ['../settings.json', '/etc/passwd', 'https://example.invalid/audio.wav']:
        assert client.post('/tts/generate', json={**payload, 'ref_audio': location}).status_code == 422
    response = client.post('/tts/generate-upload', data={'payload': json.dumps(payload)},
        files={'reference_audio': ('ref.wav', recording(), 'audio/wav')})
    assert response.status_code == 422


def test_mcp_unknown_host_is_rejected_even_when_enabled(tmp_path):
    app = create_app(Engine(), tmp_path)
    with TestClient(app, base_url='http://untrusted.example') as client:
        client.put('/system/settings', json={'mcp_enabled': True})
        response = client.post('/mcp/', json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'},
                              headers={'Accept': 'application/json, text/event-stream'})
        assert response.status_code == 421


def test_queue_overload_is_actionable_through_mcp(tmp_path):
    engine = StudioEngine(queue_capacity=0)
    app = create_app(engine, tmp_path)
    ticket = engine.admit()
    try:
        with TestClient(app) as client:
            with pytest.raises(ToolError, match='HTTP 429'):
                call(app, 'talk_simple', {'text': 'Wait your turn.'})
    finally:
        engine.cancel_admission(ticket)
    assert not engine.waiters


def test_cancelled_mcp_generation_stops_the_shared_worker(tmp_path):
    entered, stopped = threading.Event(), threading.Event()
    class Blocking(Engine):
        def generate(self, request, reference, cancelled, emit, streaming):
            entered.set()
            try:
                assert cancelled.wait(5), 'Cancelled MCP did not release generation'
            finally:
                stopped.set()
    app = create_app(Blocking(), tmp_path)
    with TestClient(app):
        async def scenario():
            task = asyncio.create_task(app.state.mcp_compact_server.call_tool('talk_simple', {'text': 'Cancel me.'}))
            assert await asyncio.to_thread(entered.wait, 3)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert await asyncio.to_thread(stopped.wait, 3)
        asyncio.run(scenario())


def test_voice_deletion_cannot_address_another_api_resource(api):
    client, _, _ = api
    script = client.post('/tts/dialogue-scripts', json={'name': 'Keep this script',
        'document': '<speak xmlns="http://www.w3.org/2001/10/synthesis">Hello.</speak>'}).json()
    with pytest.raises(ToolError, match='exact saved voice id'):
        call(client.app, 'delete_saved_voice', {'voice_id': '../dialogue-scripts/' + script['id']}, advanced=True)
    assert client.get('/tts/dialogue-scripts/' + script['id']).status_code == 200
