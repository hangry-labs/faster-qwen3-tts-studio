import base64
import io
import json
import re
import threading
import time

from fastapi.testclient import TestClient
import numpy as np
import pytest
import soundfile as sf

from faster_qwen3_tts.standalone_ui.runtime import GenerationRequest, MODELS, StudioEngine
from faster_qwen3_tts.standalone_ui.server import create_app, wav_bytes


class FakeEngine:
    def __init__(self):
        self.requests = []
        self.current = None

    def status(self):
        return {'state': 'idle', 'model': self.current, 'loaded': self.current is not None,
                'default_backend': 'torch', 'available_backends': ['torch']}

    def load(self, model):
        self.current = model
        return self.status()

    def unload(self):
        self.current = None
        return self.status()

    def generate(self, request, reference, cancelled, emit, streaming):
        self.requests.append((request, reference.read_bytes() if reference else None, streaming))
        emit({'type': 'queued', 'position': 0})
        emit({'type': 'ready', 'model': request.model})
        emit({'type': 'chunk', 'audio': np.zeros(2400, dtype=np.float32), 'sample_rate': 24000,
              'ttfa_ms': 5, 'duration_s': .1})
        emit({'type': 'done', 'metrics': {'duration_s': .1, 'generation_ms': 10, 'speed': 10, 'ttfa_ms': 5}})


@pytest.fixture
def studio(tmp_path):
    engine = FakeEngine()
    with TestClient(create_app(engine, tmp_path)) as client:
        yield client, engine


def config(mode='custom', **overrides):
    name = {'custom': '0.6B-CustomVoice', 'design': '1.7B-VoiceDesign', 'clone': '0.6B-Base'}[mode]
    return {'mode': mode, 'model': 'Qwen/Qwen3-TTS-12Hz-' + name,
            'text': 'Hello from the test voice.', **({'xvec_only': True} if mode == 'clone' else {}), **overrides}


def audio():
    return wav_bytes(np.zeros(2400, dtype=np.float32), 24000)


def test_shell_assets_and_capabilities_are_local_and_complete(studio):
    client, _ = studio
    response = client.get('/')
    assert response.status_code == 200
    assert response.headers['cache-control'] == 'no-store'
    assert '{{UI_' not in response.text
    for path in re.findall(r'(?:src|href)="(/(?:static|assets)/[^"]+)"', response.text):
        assert client.get(path).status_code == 200, path
    capabilities = client.get('/studio/capabilities').json()
    assert len(capabilities['models']) == 5
    assert capabilities['formats'] == ['wav']
    assert {item['mode'] for item in capabilities['models']} == {'custom', 'design', 'clone'}
    assert all(re.fullmatch('[a-f0-9]{40}', item['revision']) for item in capabilities['models'])
    assert 'https://cdn' not in response.text
    assert client.get('/docs', follow_redirects=False).headers['location'] == '/en#api'
    assert '/studio/generate' in client.get('/openapi.json').json()['paths']
    english_keys = set(client.get('/static/locales/en.json').json())
    for locale in ('nb', 'pl', 'ja', 'zh', 'es'):
        assert set(client.get(f'/static/locales/{locale}.json').json()) == english_keys


@pytest.mark.parametrize('overrides', [
    {'mode': 'unknown'}, {'model': 'other/model'}, {'text': ' '}, {'text': 'x' * 1001},
    {'language': 'Norwegian'}, {'speaker': 'invented'}, {'temperature': -1},
    {'instruct': 'Not supported by the 0.6B model'}, {'mode': 'design'},
])
def test_invalid_capabilities_fail_before_inference(studio, overrides):
    client, engine = studio
    result = client.post('/studio/generate', data={'options': json.dumps({**config(), **overrides})})
    assert result.status_code == 422
    assert engine.requests == []


@pytest.mark.parametrize('mode', ['custom', 'design', 'clone'])
@pytest.mark.parametrize('streaming', [False, True])
def test_all_voice_workflows_reach_the_engine(studio, mode, streaming):
    client, engine = studio
    options = config(mode, temperature=.8, top_k=30, repetition_penalty=1.1,
                     non_streaming_mode=False, chunk_size=4, seed=123)
    if mode == 'design':
        options['instruct'] = 'A gentle, clear narrator.'
    files = {'reference': ('voice.wav', audio(), 'audio/wav')} if mode == 'clone' else None
    result = client.post('/studio/generate' + ('/stream' if streaming else ''),
                         data={'options': json.dumps(options)}, files=files)
    assert result.status_code == 200, result.text
    request, reference, streamed = engine.requests[0]
    assert request.mode == mode and request.temperature == .8 and request.top_k == 30
    assert request.seed == 123 and request.chunk_size == 4 and not request.non_streaming_mode
    assert streamed is streaming
    assert bool(reference) is (mode == 'clone')
    if streaming:
        events = [json.loads(line[6:]) for line in result.text.splitlines() if line.startswith('data: ')]
        assert [event['type'] for event in events] == ['queued', 'ready', 'chunk', 'done']
        encoded = next(event['audio_b64'] for event in events if event['type'] == 'chunk')
    else:
        encoded = result.json()['audio_b64']
    samples, rate = sf.read(io.BytesIO(base64.b64decode(encoded)))
    assert rate == 24000 and len(samples) == 2400


def test_clone_requires_reference_and_accurate_transcript(studio):
    client, engine = studio
    assert client.post('/studio/generate', data={'options': json.dumps(config('clone'))}).status_code == 422
    assert client.post('/studio/generate', data={'options': json.dumps(config('clone', xvec_only=False))},
                       files={'reference': ('v.wav', audio())}).status_code == 422
    assert not engine.requests


@pytest.mark.parametrize('mode,whole_text', [('custom', True), ('design', True), ('clone', False)])
def test_workflow_defaults_preserve_explicit_text_delivery(mode, whole_text):
    options = config(mode, instruct='A gentle narrator.' if mode == 'design' else '')
    options.pop('xvec_only', None)
    if mode == 'clone':
        options['ref_text'] = 'Reference words.'
    request = GenerationRequest(**options)
    assert request.non_streaming_mode is whole_text
    if mode == 'clone':
        assert request.xvec_only is False
    assert GenerationRequest(**options, non_streaming_mode=not whole_text).non_streaming_mode is not whole_text


def test_complete_inference_can_report_queue_and_progress_events(studio):
    client, engine = studio
    result = client.post('/studio/generate/stream?streaming=false', data={'options': json.dumps(config())})
    assert result.status_code == 200
    events = [json.loads(line[6:]) for line in result.text.splitlines() if line.startswith('data: ')]
    assert [event['type'] for event in events] == ['queued', 'ready', 'chunk', 'done']
    assert events[0]['position'] == 0
    assert engine.requests[-1][2] is False


@pytest.mark.parametrize('model', ['0.6B-Base', '1.7B-Base'])
@pytest.mark.parametrize('streaming', [False, True])
@pytest.mark.parametrize('identity_only', [False, True])
def test_clone_direction_reaches_model_for_both_playback_modes(tmp_path, monkeypatch, model, streaming, identity_only):
    calls = []

    class CapturingModel:
        def generate_voice_clone(self, **kwargs):
            calls.append(kwargs)
            return [np.zeros(2400, dtype=np.float32)], 24000

        def generate_voice_clone_streaming(self, **kwargs):
            calls.append(kwargs)
            yield np.zeros(2400, dtype=np.float32), 24000, {}

    engine = StudioEngine()
    engine.model = CapturingModel()
    monkeypatch.setattr(engine, '_load', lambda name: None)
    options = config('clone', model='Qwen/Qwen3-TTS-12Hz-' + model,
                     instruct='Speak gently and slowly.', xvec_only=identity_only,
                     ref_text='' if identity_only else 'The exact reference words.')
    with TestClient(create_app(engine, tmp_path)) as client:
        spec = next(item for item in client.get('/studio/capabilities').json()['models']
                    if item['id'] == options['model'])
        assert spec['instructions'] and spec['instruction_support'] == 'experimental'
        result = client.post('/studio/generate' + ('/stream' if streaming else ''),
                             data={'options': json.dumps(options)},
                             files={'reference': ('voice.wav', audio(), 'audio/wav')})
        assert result.status_code == 200, result.text
        if streaming:
            events = [json.loads(line[6:]) for line in result.text.splitlines() if line.startswith('data: ')]
            assert events[-1]['type'] == 'done'
    assert len(calls) == 1
    assert calls[0]['instruct'] == options['instruct']
    assert calls[0]['xvec_only'] is identity_only
    assert calls[0]['ref_text'] == options['ref_text']
    assert calls[0]['ref_audio']


def test_bad_audio_and_oversized_uploads_are_rejected(studio):
    client, engine = studio
    for content in [b'invalid audio', b'x' * (10 * 1024 * 1024 + 1)]:
        result = client.post('/studio/generate', data={'options': json.dumps(config('clone'))},
                             files={'reference': ('audio.wav', content)})
        assert result.status_code == 422
    assert not engine.requests


def test_explicit_voice_library_survives_app_restart(tmp_path):
    with TestClient(create_app(FakeEngine(), tmp_path)) as client:
        saved = client.post('/studio/voices', data={'name': '../A clear voice', 'transcript': 'Hello.'},
                            files={'file': ('voice.wav', audio(), 'audio/wav')}).json()
    with TestClient(create_app(FakeEngine(), tmp_path)) as client:
        assert client.get('/studio/voices').json()['voices'] == [saved]
        assert client.get(saved['audio_url']).status_code == 200
        assert client.get('/studio/voices/not-a-voice/audio').status_code == 404
        assert client.delete('/studio/voices/' + saved['id']).status_code == 200
        assert client.get('/studio/voices').json()['voices'] == []


def test_settings_are_explicit_and_persistent(tmp_path):
    with TestClient(create_app(FakeEngine(), tmp_path)) as client:
        assert client.put('/system/settings', json={'asr_url': 'file:///private'}).status_code == 422
        assert client.put('/system/settings', json={'asr_url': 'http://localhost:8010/'}).status_code == 200
    with TestClient(create_app(FakeEngine(), tmp_path)) as client:
        assert client.get('/system/settings').json()['asr_url'] == 'http://localhost:8010'


def test_asr_requires_explicit_connection_and_can_be_disconnected(tmp_path, monkeypatch):
    monkeypatch.delenv('QWEN_STUDIO_ASR_URL', raising=False)
    with TestClient(create_app(FakeEngine(), tmp_path)) as client:
        assert client.get('/system/settings').json()['asr_url'] == ''
        assert client.get('/studio/asr/status').json()['ready'] is False
        result = client.post('/studio/asr/transcribe', files={'file': ('reference.wav', audio())})
        assert result.status_code == 503 and 'Configure an ASR' in result.json()['detail']
    monkeypatch.setenv('QWEN_STUDIO_ASR_URL', 'https://asr.example.com/')
    with TestClient(create_app(FakeEngine(), tmp_path)) as client:
        assert client.get('/system/settings').json()['asr_url'] == 'https://asr.example.com'
        assert client.put('/system/settings', json={'asr_url': ''}).status_code == 200
    with TestClient(create_app(FakeEngine(), tmp_path)) as client:
        assert client.get('/system/settings').json()['asr_url'] == ''


def test_model_load_and_unload_validate_allowed_models(studio):
    client, engine = studio
    assert client.post('/studio/models/load', json={'model': 'arbitrary/path'}).status_code == 422
    selected = next(iter(MODELS))
    assert client.post('/studio/models/load', json={'model': selected}).status_code == 200
    assert engine.current == selected
    assert client.post('/studio/models/unload').status_code == 200
    assert engine.current is None


def test_cancelled_stream_keeps_model_lock_until_generator_closes(monkeypatch):
    engine = StudioEngine()
    entered, resume, closed, unloaded = [threading.Event() for _ in range(4)]
    cancelled = threading.Event()

    class Model:
        def generate_custom_voice_streaming(self, **kwargs):
            try:
                entered.set()
                assert resume.wait(5)
                yield np.zeros(100), 24000, {}
            finally:
                closed.set()

    engine.model = Model()
    monkeypatch.setattr(engine, '_load', lambda name: None)
    monkeypatch.setattr(engine, '_unload', lambda: unloaded.set())
    worker = threading.Thread(target=engine.generate, args=(GenerationRequest(**config()), None, cancelled, lambda item: None, True))
    worker.start()
    assert entered.wait(5)
    other = threading.Thread(target=engine.unload)
    other.start()
    assert not unloaded.wait(.1)
    cancelled.set(); resume.set()
    worker.join(5); other.join(5)
    assert closed.is_set() and unloaded.is_set()
    assert not worker.is_alive() and not other.is_alive()


def test_queue_is_fifo_and_cancelling_a_waiter_updates_positions(monkeypatch):
    engine = StudioEngine()
    release = threading.Event()
    entered = threading.Event()
    order = []
    events = {name: [] for name in 'ABCD'}
    queued = {name: threading.Event() for name in 'ABCD'}
    cancelled = {name: threading.Event() for name in 'ABCD'}

    class Model:
        def generate_custom_voice(self, **kwargs):
            name = kwargs['text']
            order.append(name)
            if name == 'A':
                entered.set()
                assert release.wait(5)
            return [np.zeros(2400)], 24000

    engine.model = Model()
    monkeypatch.setattr(engine, '_load', lambda name: None)

    def run(name):
        def emit(event):
            events[name].append(event)
            if event['type'] == 'queued':
                queued[name].set()
        engine.generate(GenerationRequest(text=name), None, cancelled[name], emit, False)

    workers = {name: threading.Thread(target=run, args=(name,)) for name in 'ABCD'}
    try:
        workers['A'].start()
        assert entered.wait(3)
        for name in 'BCD':
            workers[name].start()
            assert queued[name].wait(3)
        assert engine.status()['queue_depth'] == 3
        assert events['D'][0]['position'] == 3
        cancelled['C'].set()
        workers['C'].join(3)
        assert not workers['C'].is_alive()
        deadline = time.monotonic() + 3
        while not any(event.get('position') == 2 for event in events['D']) and time.monotonic() < deadline:
            threading.Event().wait(.01)
        assert any(event.get('position') == 2 for event in events['D'])
    finally:
        release.set()
        for worker in workers.values():
            if worker.ident is not None:
                worker.join(5)
    assert order == ['A', 'B', 'D']
    assert engine.status()['queue_depth'] == 0 and not engine.gate.locked()


def test_stream_diagnostics_separate_model_reference_and_queue_times(tmp_path, monkeypatch):
    engine = StudioEngine()

    class Model:
        last_reference_preparation_ms = 3.5
        last_reference_cache_hit = True

        def generate_voice_clone_streaming(self, **kwargs):
            yield np.zeros(2400), 24000, {'prefill_ms': 10, 'decode_ms': 5}
            yield np.zeros(2400), 24000, {'prefill_ms': 0, 'decode_ms': 7}

    engine.model = Model()
    monkeypatch.setattr(engine, '_load', lambda name: None)
    reference = tmp_path / 'reference.wav'
    reference.write_bytes(audio())
    events = []
    engine.generate(GenerationRequest(**config('clone')), reference, threading.Event(), events.append, True)
    result = events[-1]['metrics']
    assert result['model_ttfa_ms'] == 15 and result['model_generation_ms'] == 22
    assert result['reference_preparation_ms'] == 3.5 and result['reference_cache_hit'] is True
    assert result['queue_ms'] >= 0 and result['model_load_ms'] >= 0
    assert result['total_ms'] >= result['generation_ms']
