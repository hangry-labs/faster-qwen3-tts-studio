"""Benchmark-only standard inference adapter, with CPU fake model outputs."""
from pathlib import Path
from unittest.mock import patch
import json

from fastapi.testclient import TestClient
import numpy as np
import torch

from benchmarks.catalog import model_ids
from benchmarks.server import NativeAdapter, NativeEngine, create_benchmark_app
from faster_qwen3_tts.standalone_ui.runtime import StudioEngine
from qwen_tts.inference.qwen3_tts_model import VoiceClonePromptItem


class Stock:
    device = 'cpu'

    def __init__(self):
        self.calls, self.preparations = [], []

    def generate_custom_voice(self, **options):
        self.calls.append(options)
        return [np.full(2400, .2, dtype=np.float32)], 24000

    generate_voice_design = generate_custom_voice
    generate_voice_clone = generate_custom_voice

    def create_voice_clone_prompt(self, **options):
        self.preparations.append(options)
        return [VoiceClonePromptItem(torch.zeros((10, 16), dtype=torch.long), torch.zeros(100),
            options['x_vector_only_mode'], not options['x_vector_only_mode'], options['ref_text'])]


def test_standard_clone_adapter_caches_by_content_across_temporary_paths(tmp_path):
    stock = Stock(); adapter = NativeAdapter(stock)
    first, second = tmp_path / 'first.wav', tmp_path / 'second.wav'
    first.write_bytes(b'fixed reference'); second.write_bytes(first.read_bytes())
    options = {'text': 'Hello.', 'ref_text': 'Reference words.', 'xvec_only': False, 'instruct': '',
        'temperature': .8, 'top_k': 40}
    adapter.generate_voice_clone(ref_audio=first, **options)
    adapter.generate_voice_clone(ref_audio=second, **options)
    assert len(stock.preparations) == 1 and adapter.last_reference_cache_hit is True
    assert stock.calls[-1]['voice_clone_prompt'][0].ref_spk_embedding.device.type == 'cpu'
    assert stock.calls[-1]['subtalker_top_k'] == 40
    assert stock.calls[-1]['subtalker_temperature'] == .8
    assert stock.calls[-1]['top_p'] == stock.calls[-1]['subtalker_top_p'] == 1
    assert 'xvec_only' not in stock.calls[-1] and 'instruct' not in stock.calls[-1]
    assert adapter.last_reference_preparation_ms >= 0
    adapter.clear_voice_prompt_cache(); assert not adapter.prompts


def test_standard_reference_cache_is_bounded_and_identity_only_has_separate_key(tmp_path):
    stock = Stock(); adapter = NativeAdapter(stock)
    for index in range(10):
        reference = tmp_path / f'{index}.wav'; reference.write_bytes(str(index).encode())
        adapter.generate_voice_clone(text='Hello.', ref_audio=reference, ref_text='Words.', xvec_only=False)
    assert len(adapter.prompts) == 8
    adapter.generate_voice_clone(text='Hello.', ref_audio=reference, ref_text='Words.', xvec_only=True)
    assert stock.preparations[-1]['x_vector_only_mode'] is True
    assert len(adapter.prompts) == 8


def test_standard_streaming_adapter_is_explicitly_one_buffered_chunk():
    stock = Stock(); adapter = NativeAdapter(stock)
    chunks = list(adapter.generate_custom_voice_streaming(text='Test.', speaker='Ryan', chunk_size=8))
    assert len(chunks) == 1
    assert chunks[0][1] == 24000 and chunks[0][2]['decode_ms'] >= 0
    assert 'chunk_size' not in stock.calls[0]


def test_native_loader_uses_local_pinned_weights_and_matching_torch_settings():
    model = model_ids('0.6B-CustomVoice')[0]
    engine = NativeEngine()
    with (patch.object(engine, '_unload'),
          patch('huggingface_hub.snapshot_download', return_value='/fixed/snapshot') as snapshot,
          patch('qwen_tts.Qwen3TTSModel.from_pretrained', return_value=Stock()) as load):
        engine._load(model)
        engine._load(model)
    assert snapshot.call_count == 1 and snapshot.call_args.kwargs['local_files_only'] is True
    assert len(snapshot.call_args.kwargs['revision']) == 40
    assert load.call_args.args == ('/fixed/snapshot',)
    assert load.call_args.kwargs == {'device_map': 'cuda:0', 'dtype': torch.bfloat16,
        'attn_implementation': 'sdpa', 'local_files_only': True}
    assert engine.status()['resident_models'] == [model]


def test_native_worker_shares_the_actual_product_planner_and_event_contract(tmp_path):
    stock = Stock(); engine = NativeEngine()
    engine.model = NativeAdapter(stock); engine.model_id = model_ids('1.7B-CustomVoice')[0]
    app = create_benchmark_app('native', engine=engine, data_dir=tmp_path)
    with TestClient(app) as client:
        info = client.get('/benchmark/info').json()
        assert info['incremental_waveforms'] is False and info['engine'] == 'native'
        options = {'model': engine.model_id, 'text': 'A test.', 'seed': 42}
        result = client.post('/tts/generate', json=options)
        assert result.status_code == 200 and result.content.startswith(b'RIFF')
        assert json.loads(result.headers['x-qwen-metrics'])['seed'] == 42
        stream = client.post('/tts/events', json=options)
        assert stream.status_code == 200
        assert stream.text.count('"type": "chunk"') == 1
        assert stream.text.count('"type": "done"') == 1
        document = '<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:h="https://hangrylabs.app/ns/ssml-h/1.0"><voice name="Ryan" h:direction="Curious and calm">Hello.</voice></speak>'
        directed = client.post('/tts/generate', json={**options, 'text': document, 'input_type': 'ssml-h'})
        assert directed.status_code == 200
        assert stock.calls[-1]['instruct'] == 'Curious and calm'
        assert stock.calls[-1]['speaker'] == 'Ryan'


def test_peak_memory_routes_do_not_initialize_cuda_on_a_cpu_worker(tmp_path):
    app = create_benchmark_app('faster', engine=StudioEngine(), data_dir=tmp_path)
    with patch.object(torch.cuda, 'is_initialized', return_value=False), TestClient(app) as client:
        result = client.post('/benchmark/memory/reset').json()
        assert result == client.get('/benchmark/memory').json()
        assert set(result) == {'allocated_mib', 'reserved_mib', 'peak_allocated_mib', 'peak_reserved_mib'}
        assert all(value == 0 for value in result.values())
