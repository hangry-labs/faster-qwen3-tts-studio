import json
from types import SimpleNamespace

from fastapi.testclient import TestClient
import numpy as np
import torch

import faster_qwen3_tts.model as model_module
from faster_qwen3_tts.model import FasterQwen3TTS
from faster_qwen3_tts.standalone_ui.server import create_app, wav_bytes
from faster_qwen3_tts.standalone_ui.runtime import StudioEngine


def model_with_extractor():
    calls = []

    def extract(**kwargs):
        calls.append(kwargs)
        identity = kwargs.get('x_vector_only_mode', False)
        return [SimpleNamespace(ref_spk_embedding=torch.zeros(1, 4),
                                ref_code=None if identity else torch.ones(3, 16, dtype=torch.long),
                                ref_text=kwargs.get('ref_text', ''))]

    base = SimpleNamespace(sample_rate=24000, create_voice_clone_prompt=extract,
                           _build_ref_text=lambda text: text,
                           _tokenize_texts=lambda texts: [torch.ones(1, 3, dtype=torch.long)])
    base._prompt_items_to_voice_clone_prompt = lambda items: {
        'ref_spk_embedding': [items[0].ref_spk_embedding], 'ref_code': [items[0].ref_code],
        'x_vector_only_mode': [False], 'icl_mode': [True]}
    return FasterQwen3TTS(base, None, None, device='cpu'), calls


def resolve(model, path, text='', identity=True, silence=True):
    return model._resolve_voice_clone_prompt_from_reference(
        input_ids=[None], ref_audio=path, ref_text=text, xvec_only=identity, append_silence=silence)


def test_identical_uploads_reuse_prompt_across_temporary_paths(tmp_path):
    model, calls = model_with_extractor()
    paths = []

    class Engine:
        def generate(self, request, reference, cancelled, emit, streaming):
            paths.append(reference)
            resolve(model, reference)
            emit({'type': 'chunk', 'audio': np.zeros(2400), 'sample_rate': 24000})
            emit({'type': 'done', 'metrics': {}})

    options = {'mode': 'clone', 'model': 'Qwen/Qwen3-TTS-12Hz-0.6B-Base',
               'text': 'Reuse the same reference.', 'xvec_only': True}
    audio = wav_bytes(np.zeros(2400), 24000)
    with TestClient(create_app(Engine(), tmp_path)) as client:
        for _ in range(2):
            response = client.post('/studio/generate', data={'options': json.dumps(options)},
                                   files={'reference': ('same.wav', audio, 'audio/wav')})
            assert response.status_code == 200, response.text
    assert paths[0] != paths[1] and not any(path.exists() for path in paths)
    assert len(calls) == 1
    assert model.voice_prompt_cache_info()['entries'] == 1
    assert model.voice_prompt_cache_info()['hits'] == 1


def test_cache_key_tracks_content_transcript_and_method(tmp_path):
    model, calls = model_with_extractor()
    path = tmp_path / 'reference.wav'
    path.write_bytes(wav_bytes(np.zeros(2400), 24000))
    resolve(model, path, text='Ignored in identity mode.')
    resolve(model, path, text='Also ignored in identity mode.')
    resolve(model, path, 'Reference one.', identity=False)
    resolve(model, path, 'Reference two.', identity=False)
    resolve(model, path, 'Reference two.', identity=False, silence=False)
    path.write_bytes(wav_bytes(np.ones(2400) * .1, 24000))
    resolve(model, path)
    assert len(calls) == 5
    assert model.voice_prompt_cache_info()['hits'] == 1
    assert calls[1]['ref_audio'][0].shape[0] == 2400 + 12000
    assert calls[3]['ref_audio'][0].shape[0] == 2400


def test_cache_is_lru_and_has_a_tensor_byte_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(model_module, 'VOICE_CACHE_ENTRIES', 2)
    model, calls = model_with_extractor()
    paths = [tmp_path / f'{index}.wav' for index in range(3)]
    for index, path in enumerate(paths):
        path.write_bytes(wav_bytes(np.ones(2400) * index / 10, 24000))
    for index in (0, 1, 0, 2, 1):
        resolve(model, paths[index])
    assert len(calls) == 4
    assert model.voice_prompt_cache_info()['entries'] == 2
    monkeypatch.setattr(model_module, 'VOICE_CACHE_BYTES', 16)
    other, _ = model_with_extractor()
    resolve(other, paths[0], 'A transcript.', identity=False)
    assert other.voice_prompt_cache_info()['entries'] == 0
    resolve(other, paths[0])
    resolve(other, paths[1])
    assert other.voice_prompt_cache_info()['bytes'] <= 16
    assert other.voice_prompt_cache_info()['entries'] == 1


def test_cached_tensors_are_detached_cpu_copies_and_hits_are_isolated(tmp_path):
    model, _ = model_with_extractor()
    path = tmp_path / 'reference.wav'
    path.write_bytes(b'an extractor stub does not need decoded audio')
    resolve(model, path)
    prompt, _, _ = resolve(model, path)
    prompt['ref_spk_embedding'][0].add_(1)
    next_prompt, _, _ = resolve(model, path)
    assert not next_prompt['ref_spk_embedding'][0].any()
    for cached_prompt, _ in model._voice_prompt_cache.values():
        tensor = cached_prompt['ref_spk_embedding'][0]
        assert tensor.device.type == 'cpu' and not tensor.requires_grad
    engine = StudioEngine()
    engine.model = model
    engine.unload()
    assert model.voice_prompt_cache_info()['entries'] == 0
    assert model.voice_prompt_cache_info()['bytes'] == 0
