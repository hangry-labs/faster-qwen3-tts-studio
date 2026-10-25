"""Voice asset provenance, atomic replacement and metadata preservation."""
import base64
import io
import json
import struct
from unittest.mock import patch

import numpy as np
import pytest
import soundfile as sf

from faster_qwen3_tts.standalone_ui.audio import wav
from faster_qwen3_tts.standalone_ui.profiles import VoiceStore
from test_speech_api import api


def recording(level=.1):
    return wav(np.full(2400, level, dtype=np.float32))


def upload(data):
    return ('reference.wav', data, 'audio/wav')


def test_profile_assets_and_type_survive_restart_and_metadata_only_edits(api, tmp_path):
    client, _, service = api
    recipe = {'version': 1, 'workflow': 'design', 'settings': {'seed': 91, 'instruct': 'Warm narrator'}, 'selected_version': 'processed'}
    response = client.post('/tts/voice-profiles', data={'name': 'Mara', 'profile_type': 'design',
        'ref_text': 'The actual words.', 'description': 'Quiet storyteller', 'tags': '["Warm", " warm ", "Narrator"]',
        'recipe': json.dumps(recipe)}, files={'reference_audio': upload(recording(.2)),
        'original_audio': upload(recording(.1)), 'processed_audio': upload(recording(.2)), 'design_audio': upload(recording(.3))})
    assert response.status_code == 200, response.text
    saved = response.json()
    assert saved['profile_type'] == 'design' and saved['tags'] == ['Warm', 'Narrator']
    assets = {key: client.get(saved[key + '_url']).content for key in ['original', 'processed', 'source']}
    assert all(assets.values()) and len(set(assets.values())) == 3
    assert all(sf.info(io.BytesIO(content)).subtype == 'FLOAT' for content in assets.values())
    selected = client.get(saved['audio_url']).content
    before = service.voices.resolve(saved['id'])
    response = client.put('/tts/voice-profiles/' + saved['id'], data={'name': 'Renamed', 'description': 'Updated'})
    assert response.status_code == 200, response.text
    after = service.voices.resolve(saved['id'])
    assert after['audio_folder'] == before['audio_folder'] and after['_asset_folders'] == before['_asset_folders']
    assert after['recipe'] == recipe and after['transcript'] == 'The actual words.' and after['profile_type'] == 'design'
    assert client.get(saved['audio_url']).content == selected
    restarted = VoiceStore(service.voices.root)
    assert restarted.resolve('renamed') == after
    for key, expected in assets.items():
        assert restarted.asset(after, key) == expected
    assert client.get('/tts/voice-profiles?q=storyteller').json()['count'] == 0
    assert client.get('/tts/voice-profiles?q=NARRATOR').json()['count'] == 1
    assert client.get('/studio/voices').json()['voices'][0]['portrait_url'] is None


def test_replacement_requires_permission_keeps_id_and_clears_stale_assets(api):
    client, _, service = api
    saved = client.post('/tts/voice-profiles', data={'name': 'Mara'}, files={
        'reference_audio': upload(recording()), 'processed_audio': upload(recording(.2)),
        'design_audio': upload(recording(.3))}).json()
    route = '/tts/voice-profiles/' + saved['id']
    before = service.voices.resolve(saved['id'])
    denied = client.put(route, data={'name': 'Mara'}, files={'reference_audio': upload(recording(.4))})
    assert denied.status_code == 422
    assert service.voices.resolve(saved['id']) == before
    denied = client.post('/tts/voice-profiles', data={'name': 'mara'}, files={'reference_audio': upload(recording(.4))})
    assert denied.status_code == 422
    replaced = client.post('/tts/voice-profiles', data={'name': 'mara', 'replace': 'true'}, files={'reference_audio': upload(recording(.4))})
    assert replaced.status_code == 200 and replaced.json()['id'] == saved['id']
    assert replaced.json()['processed_url'] is None and replaced.json()['source_url'] is None
    assert client.get(replaced.json()['original_url']).content == client.get(replaced.json()['audio_url']).content
    client.delete(route)
    assert service.voices.list() == [] and not list(service.voices.root.glob('*/'))


def test_failed_publication_rolls_back_all_new_assets(tmp_path):
    store = VoiceStore(tmp_path)
    first = store.commit([({'name': 'Mara'}, b'original', False) ])['Mara']
    folders = set(tmp_path.iterdir())
    with patch.object(store, '_publish', side_effect=OSError('disk full')):
        with pytest.raises(OSError):
            store.update(first['id'], {'name': 'Mara'}, b'new', {'portrait': b'image'})
    assert store.resolve('Mara') == first and store.audio(first) == b'original'
    assert set(tmp_path.iterdir()) == folders


def test_rename_collision_preserves_both_recordings(api):
    client, _, service = api
    a = client.post('/tts/voice-profiles', data={'name': 'Alpha'}, files={'reference_audio': upload(recording())}).json()
    client.post('/tts/voice-profiles', data={'name': 'Beta'}, files={'reference_audio': upload(recording(.2))})
    before = service.voices.list()
    assert client.put('/tts/voice-profiles/' + a['id'], data={'name': 'beta'}).status_code == 422
    assert service.voices.list() == before


@pytest.mark.parametrize('data', [{'tags': '{}'}, {'tags': '[4]'}, {'recipe': '[]'}, {'recipe': '{"x":NaN}'},
                                {'profile_type': 'weights'}, {'description': 'x' * 1501}])
def test_invalid_metadata_never_publishes(api, data):
    client, _, service = api
    response = client.post('/tts/voice-profiles', data={'name': 'Bad', **data}, files={'reference_audio': upload(recording())})
    assert response.status_code == 422 and service.voices.list() == []


def test_portrait_normalizes_to_lossless_100px_webp_and_metadata_can_clear(api):
    client, _, service = api
    # Valid 1x1 transparent PNG. Exercise real FFmpeg, including dimension checks.
    png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=')
    response = client.post('/tts/voice-profiles', data={'name': 'Portrait'}, files={
        'reference_audio': upload(recording()), 'portrait': ('portrait.png', png, 'image/png')})
    assert response.status_code == 200, response.text
    saved = response.json(); image = client.get(saved['portrait_url'])
    assert image.headers['content-type'] == 'image/webp' and image.headers['cache-control'] == 'no-store'
    assert image.content[:4] == b'RIFF' and b'VP8L' in image.content
    dimensions = struct.unpack('<I', image.content[21:25])[0]
    assert ((dimensions & 0x3fff) + 1, ((dimensions >> 14) & 0x3fff) + 1) == (100, 100)
    from faster_qwen3_tts.standalone_ui.profile_api import portrait_bytes
    assert portrait_bytes(image.content)[:4] == b'RIFF'
    response = client.put('/tts/voice-profiles/' + saved['id'], data={'name': 'Portrait', 'clear_portrait': 'true'})
    assert response.status_code == 200 and response.json()['portrait_url'] is None
    assert client.get(saved['portrait_url']).status_code == 404


@pytest.mark.parametrize('portrait', [b'<svg/>', b'\x89PNG\r\n\x1a\nbroken', b'x' * (5 * 1024 * 1024 + 1)])
def test_invalid_portraits_leave_no_saved_voice(api, portrait):
    client, _, service = api
    response = client.post('/tts/voice-profiles', data={'name': 'Bad'}, files={
        'reference_audio': upload(recording()), 'portrait': ('portrait.png', portrait, 'image/png')})
    assert response.status_code == 422 and service.voices.list() == []


def test_legacy_profiles_without_index_remain_readable_and_editable(tmp_path):
    identity = 'a' * 32
    folder = tmp_path / identity; folder.mkdir()
    (folder / 'audio.wav').write_bytes(b'legacy')
    (folder / 'voice.json').write_text(json.dumps({'id': identity, 'name': 'Legacy', 'transcript': 'Old words'}))
    store = VoiceStore(tmp_path)
    updated = store.update(identity, {'name': 'Legacy renamed', 'tags': ['vintage']})
    assert store.audio(updated) == b'legacy' and updated['transcript'] == 'Old words'
    assert updated['audio_folder'] == identity
