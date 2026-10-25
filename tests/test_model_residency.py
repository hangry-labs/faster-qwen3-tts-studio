"""Residency contracts with tiny CPU models, including multi-model requests."""
import json
import threading
from unittest.mock import patch
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from faster_qwen3_tts.standalone_ui.model_policy import DEFAULT_MODELS, ModelPolicy
from faster_qwen3_tts.standalone_ui.runtime import GenerationRequest, StudioEngine
from faster_qwen3_tts.standalone_ui.server import create_app
from faster_qwen3_tts.standalone_ui.profiles import VoiceStore
from faster_qwen3_tts.standalone_ui.speech import SpeechRequest, SpeechService
from faster_qwen3_tts import FasterQwen3TTS


class TinyModel:
    def __init__(self):
        self.cleared = False

    def warmup(self, **kwargs):
        pass

    def clear_voice_prompt_cache(self):
        self.cleared = True

    def generate_custom_voice(self, **kwargs):
        return [np.zeros(2400, dtype=np.float32)], 24000


def test_disposal_resets_captured_graph_pools_before_dropping_weights():
    resets = []
    graphs = [SimpleNamespace(graph=SimpleNamespace(reset=lambda: resets.append(True)), captured=True) for _ in range(2)]
    model = FasterQwen3TTS(SimpleNamespace(sample_rate=24000), *graphs, device='cpu')
    StudioEngine._dispose(model)
    assert len(resets) == 2
    assert model.model is model.predictor_graph is model.talker_graph is None
    assert all(graph.graph is None and not graph.captured for graph in graphs)
    model.close()
    assert len(resets) == 2


def test_blas_workspace_cleanup_waits_until_all_pins_are_disposed():
    engine = StudioEngine(); model = TinyModel()
    engine.models['pinned'] = engine.model = model
    with patch('torch.cuda.is_initialized', return_value=True), \
         patch('torch.cuda.synchronize') as synchronize, \
         patch('torch._C._cuda_clearCublasWorkspaces') as clear, \
         patch('torch.cuda.empty_cache'):
        engine._trim_cuda()
        clear.assert_not_called(); synchronize.assert_not_called()
        engine.models.clear(); engine.model = None
        engine._trim_cuda()
        synchronize.assert_called_once(); clear.assert_called_once()


@pytest.fixture
def loaders():
    created = []
    def construct(*args, **kwargs):
        model = TinyModel(); created.append(model); return model
    with patch('huggingface_hub.snapshot_download', return_value='cached'), \
         patch('faster_qwen3_tts.FasterQwen3TTS.from_pretrained', side_effect=construct):
        yield created


def test_unloading_an_idle_engine_does_not_initialize_cuda():
    engine = StudioEngine()
    with patch('torch.cuda.is_initialized', return_value=False), \
         patch('torch.cuda.synchronize') as synchronize, \
         patch('torch.cuda.empty_cache') as empty:
        engine.unload()
    synchronize.assert_not_called(); empty.assert_not_called()


def test_default_policy_keeps_three_correct_workflows_and_rejects_nonexistent_design():
    policy = ModelPolicy()
    assert len(policy.resident_models) == 3
    assert '0.6B' in policy.workflows['clone'].model
    assert '0.6B' in policy.workflows['custom'].model
    assert '1.7B' in policy.workflows['design'].model
    invalid = policy.model_dump()
    invalid['workflows']['design']['model'] = DEFAULT_MODELS['clone']
    with pytest.raises(ValidationError):
        ModelPolicy.model_validate(invalid)


def test_pinned_weights_coexist_and_reuse_across_switches(loaders):
    engine = StudioEngine(); engine.configure_models(ModelPolicy())
    assert len(loaders) == len(engine.status()['resident_models']) == 3
    first = engine.models[DEFAULT_MODELS['clone']]
    engine.load(DEFAULT_MODELS['clone']); engine.load(DEFAULT_MODELS['custom'])
    assert len(loaders) == 3 and engine.models[DEFAULT_MODELS['clone']] is first
    engine.unload()
    assert all(model.cleared for model in loaders) and not engine.models


def test_request_only_survives_full_session_and_releases_even_on_cancellation(loaders):
    policy = ModelPolicy(); policy.workflows['custom'].keep_loaded = False
    engine = StudioEngine(); engine.configure_models(policy)
    custom = DEFAULT_MODELS['custom']
    cancelled = threading.Event()
    with engine.session(cancelled, lambda event: None):
        request = GenerationRequest(text='Hello.', model=custom)
        engine.generate(request, None, cancelled, lambda event: None, False)
        assert custom in engine.models
        engine.generate(request, None, cancelled, lambda event: None, False)
        assert len(loaders) == 3
        cancelled.set()
    assert custom not in engine.models and loaders[-1].cleared
    assert set(engine.models) == policy.resident_models
    engine.configure_models(ModelPolicy(enabled=False))
    assert not engine.models
    engine.generate(request, None, threading.Event(), lambda event: None, False)
    assert not engine.models and engine.status()['state'] == 'idle'


def test_failed_preload_preserves_other_pins_and_reports_missing_weight(loaders):
    engine = StudioEngine()
    original = engine._load
    def load(model):
        if model == DEFAULT_MODELS['design']:
            raise RuntimeError('Not enough GPU memory')
        original(model)
    with patch.object(engine, '_load', side_effect=load):
        status = engine.configure_models(ModelPolicy())
    assert len(status['resident_models']) == 2
    assert DEFAULT_MODELS['design'] in status['residency_errors']
    assert status['state'] == 'error'


def test_failed_warmup_disposes_partial_models(loaders):
    engine = StudioEngine()
    with patch.object(TinyModel, 'warmup', side_effect=RuntimeError('Capture failed')):
        status = engine.configure_models(ModelPolicy())
    assert len(loaders) == 3 and all(model.cleared for model in loaders)
    assert not status['resident_models'] and len(status['residency_errors']) == 3


def test_production_startup_preloads_persisted_choices_without_blocking_shell(tmp_path, loaders):
    policy = ModelPolicy()
    policy.workflows['custom'].model = DEFAULT_MODELS['custom'].replace('0.6B', '1.7B')
    policy.workflows['clone'].keep_loaded = policy.workflows['design'].keep_loaded = False
    (tmp_path / 'settings.json').write_text(json.dumps({'model_policy': policy.model_dump()}))
    engine = StudioEngine()
    with patch('faster_qwen3_tts.standalone_ui.server.StudioEngine', return_value=engine):
        with TestClient(create_app(data_root=tmp_path)) as client:
            assert client.get('/').status_code == 200
    assert len(loaders) == 1
    assert set(engine.status()['resident_models']) == policy.resident_models


def test_settings_partial_updates_persist_policy_and_route_auto_requests(tmp_path, loaders):
    engine = StudioEngine()
    with TestClient(create_app(engine, tmp_path)) as client:
        policy = ModelPolicy(); policy.workflows['clone'].model = DEFAULT_MODELS['clone'].replace('0.6B', '1.7B')
        policy.workflows['custom'].model = DEFAULT_MODELS['custom'].replace('0.6B', '1.7B')
        policy.workflows['custom'].keep_loaded = False
        assert client.put('/system/settings', json={'asr_url': 'http://asr.example.test'}).status_code == 200
        result = client.put('/system/settings', json={'model_policy': policy.model_dump()})
        assert result.status_code == 200
        assert result.json()['asr_url'] == 'http://asr.example.test'
        assert client.get('/studio/capabilities').json()['workflow_defaults']['clone']['model'] == policy.workflows['clone'].model
        assert client.get('/studio/capabilities').json()['generation_defaults']['model'] == policy.workflows['custom'].model
        with patch.object(engine, 'generate', wraps=engine.generate) as generation:
            response = client.post('/studio/generate', data={'options': json.dumps({'text': 'Hello.'})})
            assert response.status_code == 200, response.text
            assert generation.call_args.args[0].model == policy.workflows['custom'].model
        service = SpeechService(engine, VoiceStore(tmp_path / 'profiles'))
        prepared = service.prepare(SpeechRequest(text='Hello.', ref_text='Reference.'), reference=b'fake')
        assert prepared.default.model == policy.workflows['clone'].model
        explicit = service.prepare(SpeechRequest(text='Hello.', model=DEFAULT_MODELS['clone'], ref_text='Reference.'), reference=b'fake')
        assert explicit.default.model == DEFAULT_MODELS['clone']
        bad = policy.model_dump(); bad['workflows']['clone']['model'] = 'not-a-model'
        assert client.put('/system/settings', json={'model_policy': bad}).status_code == 422
        assert client.get('/system/settings').json()['model_policy'] == policy.model_dump()
    with TestClient(create_app(StudioEngine(), tmp_path)) as client:
        assert client.get('/system/settings').json()['model_policy'] == policy.model_dump()
    saved = json.loads((tmp_path / 'settings.json').read_text())
    assert saved['model_policy'] == policy.model_dump()
