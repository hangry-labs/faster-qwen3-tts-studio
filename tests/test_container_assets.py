"""Baked assets must survive offline cache use and full/tiny volume sharing."""
import hashlib
import json
from pathlib import Path

from huggingface_hub import snapshot_download
import pytest

from faster_qwen3_tts.standalone_ui.docker_entrypoint import seed_cache
from scripts import prefetch_models


def synthetic_cache(root):
    revision = 'a' * 40
    repo = root / 'hub/models--test--voice'
    blob = repo / 'blobs/immutable'
    blob.parent.mkdir(parents=True)
    blob.write_bytes(b'test weights')
    snapshot = repo / 'snapshots' / revision
    snapshot.mkdir(parents=True)
    (snapshot / 'config.json').write_text('{}')
    (snapshot / 'README.md').write_text('License: Apache-2.0')
    (snapshot / 'model.safetensors').symlink_to('../../blobs/immutable')
    (snapshot / 'speech_tokenizer').mkdir()
    (snapshot / 'speech_tokenizer/config.json').write_text('{}')
    return revision, snapshot


def test_baked_cache_seeds_once_preserves_other_models_and_resolves_offline(tmp_path):
    source, target = tmp_path / 'baked', tmp_path / 'volume'
    revision, _ = synthetic_cache(source)
    target.mkdir()
    operator = target / 'operator-model.bin'
    operator.write_bytes(b'keep')
    assert seed_cache(source, target) > 0
    assert seed_cache(source, target) == 0
    assert operator.read_bytes() == b'keep'
    path = Path(snapshot_download('test/voice', revision=revision,
                cache_dir=target / 'hub', local_files_only=True))
    assert (path / 'model.safetensors').read_bytes() == b'test weights'
    assert (path / 'README.md').is_file()


def test_tiny_has_no_baked_cache_to_seed(tmp_path):
    assert seed_cache(tmp_path / 'absent', tmp_path / 'volume') == 0
    assert not (tmp_path / 'volume').exists()


def test_cache_merge_repairs_truncated_blob_and_same_length_metadata(tmp_path):
    source, target = tmp_path / 'baked', tmp_path / 'volume'
    revision, _ = synthetic_cache(source)
    seed_cache(source, target)
    blob = target / 'hub/models--test--voice/blobs/immutable'
    blob.write_bytes(b'bad')
    config = target / 'hub/models--test--voice/snapshots' / revision / 'config.json'
    config.write_text('[]')
    seed_cache(source, target)
    assert blob.read_bytes() == b'test weights'
    assert config.read_text() == '{}'


def test_cache_merge_accepts_existing_regular_snapshot_files(tmp_path):
    source, target = tmp_path / 'baked', tmp_path / 'volume'
    revision, _ = synthetic_cache(source)
    seed_cache(source, target)
    weight = target / 'hub/models--test--voice/snapshots' / revision / 'model.safetensors'
    weight.unlink()
    weight.write_bytes(b'test weights')
    assert seed_cache(source, target) == 0
    assert weight.read_bytes() == b'test weights'


def test_cache_symlink_cannot_write_outside_product_cache(tmp_path):
    source, target = tmp_path / 'baked', tmp_path / 'volume'
    synthetic_cache(source)
    outside = tmp_path / 'outside'
    outside.mkdir()
    target.mkdir()
    (target / 'hub').symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='escapes'):
        seed_cache(source, target)
    assert not list(outside.iterdir())


def test_prefetch_retains_cards_exact_revisions_and_file_hashes(tmp_path, monkeypatch):
    revision, snapshot = synthetic_cache(tmp_path)
    monkeypatch.setattr(prefetch_models, 'MODELS', {
        'test/voice': {'id': 'test/voice', 'revision': revision, 'license': 'Apache-2.0'}})
    calls = []
    def download(repo_id, **kwargs):
        calls.append((repo_id, kwargs))
        return str(snapshot)
    monkeypatch.setattr(prefetch_models, 'snapshot_download', download)
    records = prefetch_models.prefetch(tmp_path, offline=True)
    assert calls[0][1]['revision'] == revision
    assert calls[0][1]['local_files_only'] is True
    weight = next(f for f in records[0]['files'] if f['path'] == 'model.safetensors')
    assert weight['sha256'] == hashlib.sha256(b'test weights').hexdigest()
    assert json.loads((tmp_path / 'model-manifest.json').read_text()) == records
    (snapshot / 'README.md').unlink()
    with pytest.raises(RuntimeError, match='model card'):
        prefetch_models.prefetch(tmp_path)
