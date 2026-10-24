"""Planner, transport, profile transaction and dialogue assembly regressions."""
import base64
from contextlib import contextmanager
import io
import json
import struct
import threading
from unittest.mock import patch

from fastapi.testclient import TestClient
import numpy as np
import pytest
import soundfile as sf

from faster_qwen3_tts.standalone_ui import audio
from faster_qwen3_tts.standalone_ui.server import create_app
from faster_qwen3_tts.standalone_ui.speech import SpeechRequest, BASE, CUSTOM, DESIGN, DIRECTED


class Engine:
    def __init__(self):
        self.requests = []
        self.leases = 0

    def status(self):
        return {'state': 'idle', 'loaded': False, 'model': None, 'queue_depth': 0}

    def unload(self):
        return self.status()

    @contextmanager
    def session(self, cancelled, emit):
        self.leases += 1
        yield

    def generate(self, request, reference, cancelled, emit, streaming):
        self.requests.append((request, reference.read_bytes() if reference else None, streaming))
        emit({'type': 'ready', 'model': request.model})
        wave = np.full(2400, .2 + len(self.requests) / 100, dtype=np.float32)
        emit({'type': 'chunk', 'audio': wave, 'sample_rate': 24000, 'duration_s': .1})
        emit({'type': 'done', 'metrics': {}})


@pytest.fixture
def api(tmp_path):
    engine = Engine()
    app = create_app(engine, tmp_path)
    with TestClient(app) as client:
        yield client, engine, app.state.speech


def xml(body, metadata=''):
    return '<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:h="https://hangrylabs.app/ns/ssml-h/1.0">' + metadata + body + '</speak>'


def definition(name='Mara', scope='request', extra=''):
    return f'<metadata><h:extensions version="1.0"><h:voice-definition name="{name}" scope="{scope}" {extra}><h:description>A warm adult storyteller.</h:description><h:sample xml:lang="en-US">Hello. My name is Mara.</h:sample></h:voice-definition></h:extensions></metadata>'


def save_voice(client, name='narrator'):
    result = client.post('/tts/voice-profiles', data={'name': name, 'ref_text': 'The original words.', 'language': 'English'},
        files={'reference_audio': ('ref.wav', audio.wav(np.ones(2400, dtype=np.float32) * .1), 'audio/wav')})
    assert result.status_code == 200, result.text
    return result.json()


def test_request_progress_is_scoped_and_keeps_metrics(api):
    client, _, _ = api
    first = client.post('/tts/generate', json={'text': 'A short test.'}, headers={'X-Qwen-Request-ID': 'ui-first'})
    assert first.status_code == 200
    assert json.loads(first.headers['x-qwen-metrics'])['duration_s'] > 0
    activity = client.get('/tts/activity?request_id=ui-first').json()
    assert activity['phase'] == 'complete'
    assert activity['metrics']['duration_s'] > 0
    assert client.get('/tts/activity?request_id=other-client').json() == {}
    streamed = client.post('/tts/stream', json={'text': 'Another test.', 'stream_format': 'mp3'}, headers={'X-Qwen-Request-ID': 'ui-stream'})
    assert streamed.status_code == 200 and streamed.content
    assert client.get('/tts/activity?request_id=ui-stream').json()['phase'] == 'complete'
    assert client.get('/tts/activity?request_id=ui-first').json() == activity
    assert client.get('/tts/activity').json()['state'] == 'idle'


def test_finishing_controls_process_audio_and_shape_pitch_speed(api):
    client, engine, _ = api
    time_axis = np.arange(audio.RATE, dtype=np.float32) / audio.RATE
    source = audio.wav(.25 * np.sin(2 * np.pi * 220 * time_axis))
    options = {'method': 'ffmpeg-shape', 'preset': 'custom', 'pitch_semitones': 6,
        'speed_factor': 1.25, 'noise_reduction_db': 2, 'bass_db': 1,
        'presence_db': 1, 'dynamics': 35, 'normalize_loudness': True}
    result = client.post('/tts/postprocess-upload', data={'options': json.dumps(options)},
        files={'audio': ('source.wav', source, 'audio/wav')})
    assert result.status_code == 200, result.text
    samples, rate = sf.read(io.BytesIO(result.content))
    assert rate == audio.RATE and .7 < len(samples) / rate < .9
    peak_frequency = np.argmax(np.abs(np.fft.rfft(samples))) * rate / len(samples)
    assert 300 < peak_frequency < 325
    assert np.isfinite(samples).all() and np.max(np.abs(samples)) <= 1
    assert not engine.requests


@pytest.mark.parametrize('overrides', [{'method': 'signalsmith'}, {'noise_reduction_db': 13},
    {'bass_db': -7}, {'presence_db': 7}, {'dynamics': 101}, {'speed_factor': 2}, {'pitch_semitones': 7}])
def test_finishing_rejects_unsupported_controls_before_processing(api, overrides):
    client, engine, _ = api
    result = client.post('/tts/postprocess-upload', data={'options': json.dumps(overrides)},
        files={'audio': ('invalid.wav', b'not audio', 'audio/wav')})
    assert result.status_code == 422
    assert not engine.requests


@pytest.mark.parametrize('fmt', ['wav', 'mp3', 'opus', 'aac', 'flac', 'pcm', 'ogg'])
def test_openai_client_formats_and_aliases(api, fmt):
    client, engine, _ = api
    response = client.post('/v1/audio/speech', json={'model': 'tts-1', 'input': 'Hello, <voice> is plain text.',
        'voice': 'alloy', 'response_format': fmt, 'harmless_future_client_field': 1})
    assert response.status_code == 200, response.text
    assert response.content
    request, _, _ = engine.requests[0]
    assert request.text == 'Hello, <voice> is plain text.'
    assert request.speaker == 'Ryan'
    assert engine.leases == 1
    assert response.headers['x-qwen-sample-rate'] == ('48000' if fmt == 'opus' else '24000')
    if fmt == 'pcm':
        assert len(response.content) == 4800
    elif fmt in {'wav', 'flac'}:
        samples, rate = sf.read(io.BytesIO(response.content))
        assert len(samples) == 2400 and rate == 24000


def test_openai_auth_errors_and_discovery(api, monkeypatch):
    client, engine, _ = api
    monkeypatch.setenv('QWEN_STUDIO_API_KEY', 'unit-test-key')
    assert client.get('/v1/models').status_code == 401
    client.headers['Authorization'] = 'Bearer unit-test-key'
    assert len(client.get('/v1/models').json()['data']) == 5
    assert client.get('/v1/models/tts-1').status_code == 200
    assert client.get('/v1/models/no-such-model').status_code == 404
    assert client.get('/v1/audio/voices').json()['object'] == 'list'
    for overrides in [{'voice': 'absent'}, {'voice': {}}, {'response_format': 'bad'}, {'speed': 99}, {'stream_format': 'sse'}, {'model': 'absent'}]:
        response = client.post('/v1/audio/speech', json={'model': 'tts-1', 'input': 'Hi.', 'voice': 'Ryan', **overrides})
        assert response.status_code == 400, response.text
        assert response.json()['error']['type'] == 'invalid_request_error'
    assert not engine.requests


@pytest.mark.parametrize('body', [
    '<audio src="https://example.com/a.wav"/>', '<phoneme alphabet="ipa" ph="a">a</phoneme>',
    '<voice name="absent">Hello</voice>', '<lang xml:lang="no-NO">Hello</lang>',
    '<prosody rate="500%">Hello</prosody>', '<prosody pitch="NaN">Hello</prosody>',
    '<break time="10001ms"/>Hello', '<speak unknown="true">Hello</speak>', '<bogus>Hello</bogus>',
])
def test_markup_rejected_before_model_or_writes(api, body):
    client, engine, service = api
    result = client.post('/tts/generate', json={'text': xml(body), 'input_type': 'ssml'})
    assert result.status_code == 422, result.text
    assert not engine.requests and engine.leases == 0 and not service.voices.list()


@pytest.mark.parametrize('document', [
    '<!DOCTYPE speak [<!ENTITY x "boom">]><speak>&x;</speak>',
    '<!DOCTYPE speak SYSTEM "file:///etc/passwd"><speak>Hello</speak>',
    '<speak><speak>Oops</speak>',
    '<speak>' + '<prosody>' * 20 + 'Hello' + '</prosody>' * 20 + '</speak>',
])
def test_hardened_xml(api, document):
    client, engine, _ = api
    assert client.post('/tts/plan', json={'text': document, 'input_type': 'ssml'}).status_code == 422
    assert not engine.requests


def test_voice_language_context_and_direction(api):
    client, engine, _ = api
    saved = save_voice(client)
    document = xml('<voice name="Vivian">Chinese.</voice><lang xml:lang="en-US"><voice name="Vivian">English.</voice></lang>'
                   '<voice name="narrator" h:direction="Quietly">Cloned words.</voice>')
    response = client.post('/tts/generate', json={'text': document, 'input_type': 'ssml-h', 'seed': 123})
    assert response.status_code == 200, response.text
    requests = [item[0] for item in engine.requests]
    assert [r.language for r in requests] == ['Chinese', 'English', 'English']
    assert [r.seed for r in requests] == [123, 124, 125]
    assert requests[-1].model == BASE and requests[-1].instruct == 'Quietly'
    assert requests[-1].ref_text == 'The original words.'
    assert engine.requests[-1][1] == client.get(saved['audio_url']).content
    assert engine.leases == 1


def test_last_unit_invalidates_entire_plan(api):
    client, engine, _ = api
    document = xml('<voice name="Ryan">Valid.</voice><voice name="Vivian" h:direction="Softly">Invalid with this model.</voice>')
    result = client.post('/tts/generate', json={'text': document, 'input_type': 'ssml-h', 'model': CUSTOM})
    assert result.status_code == 422 and engine.leases == 0


@pytest.mark.parametrize('streaming', [False, True])
def test_dynamic_voice_bootstrap_reused_and_profile_published_after_success(api, streaming):
    client, engine, service = api
    document = xml('<voice name="Mara">First.</voice><break time="0ms"/><voice name="Mara" h:direction="Calm">Second.</voice>', definition(scope='profile', extra='seed="72"'))
    payload = {'text': document, 'input_type': 'ssml-h', 'seed': 20}
    response = client.post('/tts/events' if streaming else '/tts/generate', json=payload)
    assert response.status_code == 200, response.text
    assert [r.model for r, _, _ in engine.requests] == [DESIGN, BASE, BASE]
    assert engine.requests[0][0].seed == 72
    assert engine.requests[1][1] == engine.requests[2][1]
    assert engine.requests[2][0].instruct == 'Calm'
    assert len(service.voices.list()) == 1
    assert service.voices.list()[0]['transcript'] == 'Hello. My name is Mara.'
    assert engine.leases == 1
    if streaming:
        events = [json.loads(l[6:]) for l in response.text.splitlines() if l.startswith('data: ')]
        assert events[-1]['type'] == 'done' and events[-1]['committed_profiles']['Mara']
        chunks = [sf.read(io.BytesIO(base64.b64decode(e['audio_b64'])))[0] for e in events if e['type'] == 'chunk']
        assert sum(len(c) for c in chunks) == 4800


def test_failed_encoding_or_preview_cannot_publish_profiles(api):
    client, _, service = api
    payload = {'text': xml('<voice name="Mara">Hi.</voice>', definition(scope='profile')), 'input_type': 'ssml-h'}
    response = client.post('/tts/magic/take', json={'payload': payload, 'speech_index': 0})
    assert response.status_code == 200 and not service.voices.list()
    with patch.object(audio, 'encode', side_effect=ValueError('Encoder failed')):
        response = client.post('/tts/generate', json=payload)
    assert response.status_code == 422 and not service.voices.list()


def test_cancellation_leaves_no_profile_or_gpu_lease(api):
    _, engine, service = api
    prepared = service.prepare(SpeechRequest(text=xml('<voice name="Mara">First.</voice><voice name="Mara">Second.</voice>',
                                                     definition(scope='profile')), input_type='ssml-h'))
    cancelled = threading.Event()
    def receive(event):
        if event['type'] == 'chunk':
            cancelled.set()
    with pytest.raises(InterruptedError):
        service.run(prepared, cancelled, receive)
    assert not service.voices.list()
    assert engine.leases == 1


def test_profile_batch_and_rename_are_atomic(api):
    client, _, service = api
    saved = save_voice(client)
    content = audio.wav(np.ones(2400, dtype=np.float32) * .1)
    with pytest.raises(ValueError):
        service.voices.commit([({'name': 'new'}, content, False), ({'name': 'narrator'}, content, False)])
    assert [v['name'] for v in service.voices.list()] == ['narrator']
    with pytest.raises(ValueError):
        service.voices.update(saved['id'], {'name': 'renamed', 'transcript': 'x' * 4001})
    assert service.voices.resolve(saved['id'])['name'] == 'narrator'


def test_magic_retained_takes_and_assembly_are_exact(api):
    client, engine, _ = api
    wave = audio.wav(np.ones(2400, dtype=np.float32) * .33)
    payload = {'text': xml('<s>Hello.</s><break time="250ms"/><s>World.</s>'), 'input_type': 'ssml-h', 'seed': 5}
    response = client.post('/tts/magic/render', data={'payload': json.dumps(payload), 'speech_ids': '["a","b"]', 'retained': '[{"id":"a","seed":9}]'},
                           files={'takes': ('retained.wav', wave, 'audio/wav')})
    assert response.status_code == 200, response.text
    assert len(engine.requests) == 1 and engine.requests[0][0].text == 'World.'
    length = struct.unpack('<I', response.content[:4])[0]
    manifest = json.loads(response.content[4:4+length])
    assert manifest['takes'][0]['seed'] == 9 and manifest['takes'][1]['seed'] == 6
    item = manifest['output']; offset = 4+length+item['offset']
    samples, rate = sf.read(io.BytesIO(response.content[offset:offset+item['length']]))
    assert len(samples) == 2400 * 2 + 6000
    assert np.all(samples[2400:8400] == 0)
    result = client.post('/tts/magic/assemble-upload', data={'options': json.dumps({'items': [{'type': 'speech', 'id': 'a'}, {'type': 'break', 'milliseconds': 0}, {'type': 'speech', 'id': 'b'}]}),
        'take_metadata': '[{"id":"a"},{"id":"b"}]'}, files=[('takes', ('a.wav', wave)), ('takes', ('b.wav', wave))])
    assert result.status_code == 200, result.text
    assert len(sf.read(io.BytesIO(result.content))[0]) == 4800


def test_profile_edit_name_and_speech_id_object(api):
    client, engine, service = api
    saved = save_voice(client)
    result = client.put('/tts/voice-profiles/' + saved['id'], data={'name': 'new-name', 'ref_text': 'Original text.'})
    assert result.status_code == 200, result.text
    assert len(service.voices.list()) == 1
    assert service.voices.list()[0]['id'] == saved['id']
    response = client.post('/v1/audio/speech', json={'model': 'qwen3-tts', 'input': 'New words.', 'voice': {'id': saved['id']}, 'response_format': 'wav', 'instructions': 'Warmly'})
    assert response.status_code == 200, response.text
    assert engine.requests[0][0].model == BASE and engine.requests[0][0].instruct == 'Warmly'
    assert client.delete('/tts/voice-profiles/' + saved['id']).status_code == 200


def test_scripts_folders_and_workspace_survive_restart(api, tmp_path):
    client, _, _ = api
    folder = client.post('/tts/dialogue-script-folders', json={'name': 'Stories'}).json()
    document = xml('<s>Hello.</s>')
    saved = client.post('/tts/dialogue-workspaces', data={'metadata': json.dumps({'name': 'a-story', 'document': document, 'folder': folder['id'],
        'workspace': {'takes': [{'speech_index': 0, 'seed': 3, 'locked': True}]}})},
        files={'takes': ('take.wav', audio.wav(np.ones(2400, dtype=np.float32) * .1))})
    assert saved.status_code == 200, saved.text
    with TestClient(create_app(Engine(), tmp_path)) as restarted:
        record = restarted.get('/tts/dialogue-scripts/a-story').json()
        assert record['document'].strip() == document
        assert record['workspace']['takes'][0]['locked']
        assert restarted.get(record['workspace']['takes'][0]['url']).status_code == 200
        assert restarted.get(record['download_url']).status_code == 200
        assert restarted.patch('/tts/dialogue-scripts/a-story/folder', json={'folder': ''}).status_code == 200
        assert restarted.delete('/tts/dialogue-scripts/a-story').status_code == 200
        assert restarted.delete('/tts/dialogue-script-folders/stories').status_code == 200


def test_generated_aac_can_be_saved_in_a_workspace(api):
    client, _, _ = api
    encoded = audio.encode(np.ones(2400, dtype=np.float32) * .1, 'aac')
    saved = client.post('/tts/dialogue-workspaces', data={'metadata': json.dumps({'name': 'aac-output',
        'document': xml('<s>Hello.</s>'), 'workspace': {'output': {'extension': 'aac'}}})},
        files={'output': ('output.aac', encoded, 'audio/aac')})
    assert saved.status_code == 200, saved.text
    response = client.get(saved.json()['workspace']['output']['url'])
    samples, rate = sf.read(io.BytesIO(response.content))
    assert len(samples) >= 2400 and rate == 24000


def test_prosody_inheritance_text_order_and_explicit_gaps(api):
    client, _, service = api
    prepared = service.prepare(SpeechRequest(text='<speak>One <prosody rate="fast"><sub alias="two">2</sub><prosody volume="soft"> three</prosody></prosody> four<break time="0ms"/>five</speak>', input_type='ssml'))
    assert [u.text.strip() for u in prepared.plan.units if u.kind == 'speech'] == ['One', 'two', 'three', 'four', 'five']
    assert prepared.plan.units[1].prosody.rate == 1.25
    assert prepared.plan.units[2].prosody.volume == .7
    source = np.r_[np.zeros(2400), np.ones(2400) * .2, np.zeros(2400)].astype(np.float32)
    implicit = np.concatenate(list(audio.assemble([('speech', source), ('speech', source)])))
    explicit = np.concatenate(list(audio.assemble([('speech', source), ('break', 250), ('speech', source)])))
    zero = np.concatenate(list(audio.assemble([('speech', source), ('break', 0), ('speech', source)])))
    assert len(implicit) - len(zero) == 2880
    assert len(explicit) - len(zero) == 6000
    assert np.array_equal(explicit[:2400], source[:2400])
    assert np.array_equal(explicit[-2400:], source[-2400:])


def test_one_unit_stream_and_complete_share_exact_effects(api):
    client, _, _ = api
    payload = {'text': '<speak><prosody rate="125%" pitch="+2st" volume="soft">Hello.</prosody></speak>', 'input_type': 'ssml', 'seed': 4}
    complete = client.post('/tts/generate', json=payload)
    streamed = client.post('/tts/events', json=payload)
    assert complete.status_code == streamed.status_code == 200
    event = next(json.loads(l[6:]) for l in streamed.text.splitlines() if l.startswith('data: ') and json.loads(l[6:])['type'] == 'chunk')
    # Fake engine changes amplitude each call; timing and duration must still match.
    a, rate = sf.read(io.BytesIO(complete.content))
    b, _ = sf.read(io.BytesIO(base64.b64decode(event['audio_b64'])))
    assert len(a) == len(b) and rate == 24000
