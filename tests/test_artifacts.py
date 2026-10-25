from __future__ import annotations

import json
import tempfile
from unittest.mock import patch
from pathlib import Path

import pytest

from faster_qwen3_tts.standalone_ui.artifacts import ArtifactExpiredError, ArtifactNotFoundError, ArtifactStore


def create_artifact(store: ArtifactStore, *, now: float = 1000):
    return store.create(
        b"audio",
        extension="mp3",
        ttl_seconds=300,
        format="mp3",
        mime_type="audio/mpeg",
        duration_seconds=1.25,
        sample_rate=24_000,
        seed=42,
        voice_mode="random",
        voice="auto",
        language="auto",
        now=now,
    )


def test_artifact_metadata_never_contains_input_text_or_audio() -> None:
    with tempfile.TemporaryDirectory() as directory:
        store = ArtifactStore(directory)
        artifact = create_artifact(store)
        resolved, path = store.resolve(artifact.token, now=1200)
        metadata = json.loads((Path(directory) / f"{artifact.token}.json").read_text(encoding="utf-8"))

        assert path.read_bytes() == b"audio"
        assert resolved.size_bytes == 5
        assert "text" not in metadata
        assert "audio" not in metadata


def test_expired_artifact_is_removed() -> None:
    with tempfile.TemporaryDirectory() as directory:
        store = ArtifactStore(directory)
        artifact = create_artifact(store)
        with pytest.raises(ArtifactExpiredError, match="expired"):
            store.resolve(artifact.token, now=1300)
        assert not any(Path(directory).iterdir())


def test_invalid_token_cannot_escape_output_directory() -> None:
    with tempfile.TemporaryDirectory() as directory:
        store = ArtifactStore(directory)
        with pytest.raises(ArtifactNotFoundError, match="not found"):
            store.resolve("../settings", now=1000)


def test_storage_limits_preserve_existing_links(tmp_path):
    store = ArtifactStore(tmp_path, max_bytes=8, max_files=1)
    first = create_artifact(store)
    with pytest.raises(ValueError, match='full'):
        create_artifact(store, now=1001)
    assert store.resolve(first.token, now=1001)[1].read_bytes() == b'audio'
    assert store.cleanup_expired(now=1300) == 1
    assert create_artifact(store, now=1301).size_bytes == 5


def test_failed_metadata_write_removes_unpublished_audio(tmp_path):
    store = ArtifactStore(tmp_path)
    write = store._atomic_write
    def fail_metadata(path, content):
        if path.suffix == '.json':
            raise OSError('disk full')
        return write(path, content)
    with patch.object(store, '_atomic_write', side_effect=fail_metadata):
        with pytest.raises(OSError):
            create_artifact(store)
    assert not list(tmp_path.iterdir())


def test_corrupt_metadata_cannot_delete_outside_the_store(tmp_path):
    output = tmp_path / 'output'; store = ArtifactStore(output)
    secret = tmp_path / 'settings.json'; secret.write_text('preserve me')
    (output / 'corrupt.json').write_text(json.dumps({'token': '../settings', 'expires_at': 0, 'filename': '../settings.json'}))
    assert store.cleanup_expired(now=1000) == 1
    assert secret.read_text() == 'preserve me'
