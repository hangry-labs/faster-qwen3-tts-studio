"""OpenAI voice lifecycle against the shared library, without model downloads."""
from concurrent.futures import ThreadPoolExecutor
import io
from unittest.mock import patch

import numpy as np
import pytest
import soundfile as sf

from faster_qwen3_tts.standalone_ui.profiles import VoiceStore
from faster_qwen3_tts.standalone_ui.server import create_app
from faster_qwen3_tts.standalone_ui.speech import BASE, DESIGN, SpeechRequest
from fastapi.testclient import TestClient
from test_speech_api import api, save_voice
from test_voice_library import recording, upload


def consent(client, name='Speaker approval'):
    response = client.post('/v1/audio/voice_consents', data={'name': name, 'language': 'en-US'},
                           files={'recording': upload(recording())})
    assert response.status_code == 200, response.text
    return response.json()


def create_voice(client, approval, name='API voice', **extra):
    return client.post('/v1/audio/voices', data={'name': name, 'consent': approval['id'], **extra},
                       files={'audio_sample': upload(recording(.2))})


def test_sample_voice_is_same_library_and_immediately_usable_with_id(api):
    client, engine, service = api
    approval = consent(client)
    result = create_voice(client, approval, ref_text='Original words.').json()
    assert set(result) == {'id', 'object', 'created_at', 'name', 'type'}
    assert result['object'] == 'audio.voice' and result['type'] == 'audio_sample'
    assert isinstance(result['created_at'], int) and result['created_at'] > 0
    saved = service.voices.resolve(result['id'])
    assert saved['consent'] == approval['id'] and saved['transcript'] == 'Original words.'
    assert client.get('/tts/voice-profiles').json()['data'][0]['id'] == result['id']
    assert any(v['id'] == result['id'] for v in client.get('/v1/audio/voices').json()['data'])
    response = client.post('/v1/audio/speech', json={'model': 'tts-1', 'voice': {'id': result['id']},
        'input': 'New words.', 'response_format': 'wav'})
    assert response.status_code == 200, response.text
    assert engine.requests[-1][0].model == BASE and not engine.requests[-1][0].xvec_only
    assert engine.requests[-1][1] == service.voices.audio(saved)


def test_missing_reference_transcript_selects_identity_only_clone(api):
    client, engine, _ = api
    saved = create_voice(client, consent(client)).json()
    response = client.post('/v1/audio/speech', json={'model': 'tts-1', 'voice': {'id': saved['id']},
        'input': 'Hello.', 'response_format': 'wav'})
    assert response.status_code == 200
    assert engine.requests[-1][0].xvec_only


def test_delete_requires_exact_id_and_leaves_consent_and_prepared_requests(api):
    client, _, service = api
    approval = consent(client)
    saved = create_voice(client, approval).json()
    prepared = service.prepare(SpeechRequest(text='Hello.', voice=saved['id']))
    reference = prepared.default.reference
    assert reference
    for identity in ['API voice', 'Ryan', 'alloy', 'absent']:
        assert client.delete('/v1/audio/voices/' + identity).status_code == 404
    response = client.delete('/v1/audio/voices/' + saved['id'])
    assert response.json() == {'id': saved['id'], 'deleted': True, 'object': 'audio.voice.deleted'}
    assert not service.voices.list() and prepared.default.reference == reference
    assert client.get('/v1/audio/voice_consents/' + approval['id']).status_code == 200
    assert client.delete('/v1/audio/voices/' + saved['id']).status_code == 404
    assert client.post('/v1/audio/speech', json={'model': 'tts-1', 'voice': saved['id'], 'input': 'Hi.'}).status_code == 400


def test_existing_native_voice_can_be_deleted_through_openai(api):
    client, _, service = api
    saved = save_voice(client)
    assert client.delete('/v1/audio/voices/' + saved['id']).status_code == 200
    assert not service.voices.list()


def test_conflicting_name_never_overwrites_recording_or_metadata(api):
    client, _, service = api
    saved = save_voice(client)
    before = service.voices.resolve(saved['id'])
    wave = service.voices.audio(before)
    assert create_voice(client, consent(client), name='NARRATOR').status_code == 409
    assert service.voices.resolve(saved['id']) == before and service.voices.audio(before) == wave


@pytest.mark.parametrize('name', ['Ryan', 'ALLOY', 'ryan'])
def test_native_names_and_aliases_cannot_be_shadowed(api, name):
    client, engine, service = api
    assert create_voice(client, consent(client), name=name).status_code == 409
    assert not service.voices.list() and not engine.requests


def test_unicode_name_and_maximum_name_survive_restart(api):
    client, _, service = api
    name = '声' * 256
    saved = create_voice(client, consent(client), name=name).json()
    assert saved['name'] == name
    restarted = VoiceStore(service.voices.root)
    assert restarted.resolve(saved['id'])['name'] == name
    assert client.delete('/v1/audio/voices/' + saved['id']).status_code == 200


@pytest.mark.parametrize('extra', [{'name': ' '}, {'name': 'a' * 257}, {'type': 'other'},
    {'consent': 'absent'}, {'consent': ''}, {'prompt': 'different source'}, {'model': '2026-10-08'}])
def test_invalid_sample_requests_do_not_publish(api, extra):
    client, _, service = api
    response = create_voice(client, consent(client), **extra)
    assert response.status_code in {400, 404}, response.text
    assert response.json()['error']['type'] == 'invalid_request_error'
    assert not service.voices.list()


def test_sample_requires_real_file_and_rejects_invalid_and_oversized_audio(api):
    client, _, service = api
    fields = {'name': 'Example', 'consent': consent(client)['id']}
    assert client.post('/v1/audio/voices', json=fields).status_code == 400
    for content in [b'', b'not audio', b'x' * (10 * 1024 * 1024 + 1)]:
        response = client.post('/v1/audio/voices', data=fields, files={'audio_sample': upload(content)})
        assert response.status_code in {400, 422}, response.text
    assert not service.voices.list()


def test_failed_voice_publication_removes_new_assets_and_retains_consent(api):
    client, _, service = api
    approval = consent(client)
    save_voice(client)
    before = service.voices.list()
    folders = set(service.voices.root.iterdir())
    with patch.object(service.voices, '_publish', side_effect=OSError('disk full')):
        response = create_voice(client, approval)
    assert response.status_code == 500
    assert service.voices.list() == before and set(service.voices.root.iterdir()) == folders
    assert client.get('/v1/audio/voice_consents/' + approval['id']).status_code == 200


def test_concurrent_creates_publish_only_one_voice(api):
    client, _, service = api
    approval = consent(client)
    with ThreadPoolExecutor(2) as pool:
        statuses = list(pool.map(lambda _: create_voice(client, approval).status_code, range(2)))
    assert sorted(statuses) == [200, 409]
    assert len(service.voices.list()) == 1


def test_consent_lifecycle_pagination_and_independent_deletion(api):
    client, _, service = api
    approvals = [consent(client, 'Same label') for _ in range(3)]
    saved = create_voice(client, approvals[0]).json()
    first = client.get('/v1/audio/voice_consents?limit=2').json()
    assert first['object'] == 'list' and first['has_more']
    assert first['first_id'] == approvals[0]['id'] and first['last_id'] == approvals[1]['id']
    second = client.get('/v1/audio/voice_consents', params={'limit': 2, 'after': first['last_id']}).json()
    assert second['data'] == [approvals[2]] and not second['has_more']
    update = client.post('/v1/audio/voice_consents/' + approvals[0]['id'], json={'name': 'New label'}).json()
    assert update == {**approvals[0], 'name': 'New label'}
    assert client.get('/v1/audio/voice_consents/' + approvals[0]['id']).json() == update
    delete = client.delete('/v1/audio/voice_consents/' + approvals[0]['id'])
    assert delete.json() == {'id': approvals[0]['id'], 'deleted': True, 'object': 'audio.voice_consent'}
    assert service.voices.resolve(saved['id'])
    assert client.get('/v1/audio/voice_consents/' + approvals[0]['id']).status_code == 404
    assert create_voice(client, approvals[0], name='Another').status_code == 404
    for verb in ['get', 'delete']:
        assert getattr(client, verb)('/v1/audio/voice_consents/absent').status_code == 404
    assert client.post('/v1/audio/voice_consents/absent', json={'name': 'New'}).status_code == 404
    assert client.get('/v1/audio/voice_consents?after=absent').status_code == 404
    assert client.get('/v1/audio/voice_consents?limit=101').status_code == 400


def test_consent_restart_and_failed_metadata_publication(api, tmp_path):
    client, engine, service = api
    approval = consent(client)
    approval_store = client.app.state.voice_consents
    record = approval_store.resolve(approval['id'][5:])
    original = approval_store.audio(record)
    with patch.object(approval_store, '_publish', side_effect=OSError('disk full')):
        response = client.post('/v1/audio/voice_consents/' + approval['id'], json={'name': 'Changed'})
    assert response.status_code == 500
    assert approval_store.audio(record) == original
    with TestClient(create_app(engine, service.voices.root.parent)) as restarted:
        assert restarted.get('/v1/audio/voice_consents/' + approval['id']).json() == approval


@pytest.mark.parametrize('body', [{'name': ' ', 'language': 'en-US'}, {'name': 'Name', 'language': '../en'},
                               {'name': 'Name', 'language': ''}])
def test_invalid_consent_metadata_never_publishes(api, body):
    client, _, _ = api
    response = client.post('/v1/audio/voice_consents', data=body, files={'recording': upload(recording())})
    assert response.status_code == 400
    assert client.get('/v1/audio/voice_consents').json()['data'] == []


@pytest.mark.parametrize('multipart', [False, True])
def test_prompt_creation_uses_design_and_saves_reference_and_recipe(api, multipart):
    client, engine, service = api
    fields = {'type': 'prompt', 'name': 'Designed', 'prompt': 'Warm and calm.', 'script_hint': 'Hello from this new voice.'}
    response = client.post('/v1/audio/voices', data=fields) if multipart else client.post('/v1/audio/voices', json=fields)
    assert response.status_code == 200, response.text
    saved = response.json()
    assert saved['type'] == 'prompt' and saved['prompt'] == fields['prompt'] and saved['object'] == 'audio.voice'
    assert engine.requests[-1][0].model == DESIGN and engine.requests[-1][0].instruct == fields['prompt']
    record = service.voices.resolve(saved['id'])
    assert record['profile_type'] == 'design' and record['recipe']['settings']['text'] == fields['script_hint']
    assert record['transcript'] == fields['script_hint'] and service.voices.audio(record)


def test_prompt_maximum_and_default_script_are_supported(api):
    client, engine, _ = api
    response = client.post('/v1/audio/voices', json={'type': 'prompt', 'name': 'Long prompt', 'prompt': 'a' * 2000})
    assert response.status_code == 200, response.text
    assert len(engine.requests[-1][0].instruct) == 2000 and engine.requests[-1][0].text


@pytest.mark.parametrize('extra', [{'prompt': ''}, {'prompt': ' '}, {'prompt': 'a' * 2001},
    {'script_hint': ' '}, {'consent': 'cons_unknown'}, {'model': '2026-10-08'}])
def test_invalid_prompt_does_not_infer_or_publish(api, extra):
    client, engine, service = api
    response = client.post('/v1/audio/voices', json={'type': 'prompt', 'name': 'Invalid', 'prompt': 'Warm voice', **extra})
    assert response.status_code == 400
    assert not engine.requests and not service.voices.list()


def test_failed_prompt_generation_never_publishes(api):
    client, engine, service = api
    with patch.object(engine, 'generate', side_effect=RuntimeError('GPU error')):
        response = client.post('/v1/audio/voices', json={'type': 'prompt', 'name': 'Failed', 'prompt': 'Warm voice'})
    assert response.status_code >= 400
    assert not service.voices.list()


def test_native_metadata_edit_preserves_prompt_but_audio_replacement_invalidates_it(api):
    client, _, service = api
    created = client.post('/v1/audio/voices', json={'type': 'prompt', 'name': 'Designed', 'prompt': 'Warm voice'}).json()
    route = '/tts/voice-profiles/' + created['id']
    assert client.put(route, data={'name': 'Renamed'}).status_code == 200
    listed = next(v for v in client.get('/v1/audio/voices').json()['data'] if v['id'] == created['id'])
    assert listed['type'] == 'prompt' and listed['prompt'] == 'Warm voice'
    assert client.put(route, data={'name': 'Renamed', 'replace_audio': 'true'},
                      files={'reference_audio': upload(recording(.3))}).status_code == 200
    listed = next(v for v in client.get('/v1/audio/voices').json()['data'] if v['id'] == created['id'])
    assert listed['type'] == 'audio_sample' and 'prompt' not in listed
    assert 'prompt' not in service.voices.resolve(created['id'])


def test_prompt_reference_preserves_float_precision(api):
    client, _, service = api
    created = client.post('/v1/audio/voices', json={'type': 'prompt', 'name': 'Designed', 'prompt': 'Warm voice'}).json()
    content = service.voices.audio(service.voices.resolve(created['id']))
    assert sf.info(io.BytesIO(content)).subtype == 'FLOAT'


def test_all_new_routes_inherit_openai_auth_and_error_envelopes(api, monkeypatch):
    client, engine, service = api
    monkeypatch.setenv('QWEN_STUDIO_API_KEY', 'test-secret')
    for method,path in [('post','/v1/audio/voices'),('delete','/v1/audio/voices/absent'),
        ('post','/v1/audio/voice_consents'),('get','/v1/audio/voice_consents'),
        ('get','/v1/audio/voice_consents/absent'),('post','/v1/audio/voice_consents/absent'),
        ('delete','/v1/audio/voice_consents/absent')]:
        response = getattr(client,method)(path)
        assert response.status_code == 401 and response.json()['error']['type'] == 'authentication_error'
    assert client.get('/v1/audio/voice_consents', headers={'Authorization':'Bearer test-secret'}).status_code == 200
    assert not service.voices.list() and not engine.requests


def test_openapi_describes_file_and_prompt_create_contracts(api):
    client, _, _ = api
    paths = client.get('/openapi.json').json()['paths']
    content = paths['/v1/audio/voices']['post']['requestBody']['content']
    assert content['multipart/form-data']['schema']['properties']['audio_sample']['format'] == 'binary'
    prompt_schema = content['application/json']['schema']['properties']['prompt']
    assert any(part.get('maxLength') == 2000 for part in prompt_schema['anyOf'])
    assert 'delete' in paths['/v1/audio/voices/{voice_id}']
