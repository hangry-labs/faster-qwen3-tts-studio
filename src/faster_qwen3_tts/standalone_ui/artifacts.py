"""Expiring capability links. Adapted from Apache-2.0 VoxCPMTTS; see NOTICE."""

from __future__ import annotations

import json
import math
import os
import secrets
import tempfile
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ARTIFACT_DIRECTORY = "/app/persistent/studio/mcp-output"
MIN_ARTIFACT_TTL_SECONDS = 60
MAX_ARTIFACT_TTL_SECONDS = 86_400


@dataclass(frozen=True)
class GeneratedArtifact:
    token: str
    filename: str
    created_at: float
    expires_at: float
    format: str
    mime_type: str
    size_bytes: int
    duration_seconds: float
    sample_rate: int
    seed: int
    voice_mode: str
    voice: str
    language: str
    created_profiles: list[str]

    def public_metadata(self, download_url: str) -> dict[str, Any]:
        return {
            "download_url": download_url,
            "expires_at": datetime.fromtimestamp(self.expires_at, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            "ttl_seconds": max(0, round(self.expires_at - self.created_at)),
            "format": self.format,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "seed": self.seed,
            "voice_mode": self.voice_mode,
            "voice": self.voice,
            "language": self.language,
            "created_profiles": list(self.created_profiles),
        }


class ArtifactNotFoundError(FileNotFoundError):
    pass


class ArtifactExpiredError(FileNotFoundError):
    pass


class ArtifactStore:
    """Persist generated files and enforce their expiry on every read."""

    def __init__(self, directory: str | Path | None = None, *, max_bytes: int = 512 * 1024 * 1024, max_files: int = 512) -> None:
        configured = directory or os.getenv("QWEN_STUDIO_MCP_OUTPUT_DIR", DEFAULT_ARTIFACT_DIRECTORY)
        self.directory = Path(configured).resolve()
        if max_bytes < 1 or max_files < 1:
            raise ValueError('Artifact storage limits must be positive.')
        self.max_bytes, self.max_files = max_bytes, max_files
        self._lock = threading.RLock()
        self.directory.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        audio: bytes,
        *,
        extension: str,
        ttl_seconds: int,
        format: str,
        mime_type: str,
        duration_seconds: float,
        sample_rate: int,
        seed: int,
        voice_mode: str,
        voice: str,
        language: str,
        created_profiles: list[str] | None = None,
        now: float | None = None,
    ) -> GeneratedArtifact:
        if not MIN_ARTIFACT_TTL_SECONDS <= ttl_seconds <= MAX_ARTIFACT_TTL_SECONDS:
            raise ValueError(f"ttl_seconds must be between {MIN_ARTIFACT_TTL_SECONDS} and {MAX_ARTIFACT_TTL_SECONDS}.")
        timestamp = datetime.now(tz=timezone.utc).timestamp() if now is None else now
        token = secrets.token_urlsafe(32)
        if extension not in {'wav', 'mp3', 'flac', 'ogg', 'opus', 'aac', 'pcm'}:
            raise ValueError('Unsupported artifact extension.')
        filename = f"qwen3tts-{token}.{extension}"
        artifact = GeneratedArtifact(
            token=token,
            filename=filename,
            created_at=timestamp,
            expires_at=timestamp + ttl_seconds,
            format=format,
            mime_type=mime_type,
            size_bytes=len(audio),
            duration_seconds=round(duration_seconds, 3),
            sample_rate=sample_rate,
            seed=seed,
            voice_mode=voice_mode,
            voice=voice,
            language=language,
            created_profiles=list(created_profiles or []),
        )
        with self._lock:
            self.cleanup_expired(now=timestamp)
            files = [p for p in self.directory.iterdir() if p.is_file() and p.suffix != '.json']
            if len(files) >= self.max_files or sum(p.stat().st_size for p in files) + len(audio) > self.max_bytes:
                raise ValueError('Temporary audio storage is full. Wait for links to expire or shorten the recording.')
            try:
                self._atomic_write(self.directory / filename, audio)
                self._atomic_write(self._metadata_path(token),
                    (json.dumps(asdict(artifact), sort_keys=True) + "\n").encode("utf-8"))
            except BaseException:
                (self.directory / filename).unlink(missing_ok=True)
                self._metadata_path(token).unlink(missing_ok=True)
                raise
        return artifact

    def resolve(self, token: str, *, now: float | None = None) -> tuple[GeneratedArtifact, Path]:
        timestamp = datetime.now(tz=timezone.utc).timestamp() if now is None else now
        if not token or any(character not in _TOKEN_CHARACTERS for character in token):
            raise ArtifactNotFoundError("Generated audio link was not found.")
        with self._lock:
            metadata_path = self._metadata_path(token)
            if not metadata_path.is_file():
                raise ArtifactNotFoundError("Generated audio link was not found.")
            try:
                payload = json.loads(metadata_path.read_text(encoding="utf-8"))
                artifact = GeneratedArtifact(**payload)
            except (OSError, json.JSONDecodeError, TypeError) as exc:
                self._remove_token(token)
                raise ArtifactNotFoundError("Generated audio metadata was invalid and has been removed.") from exc
            path = (self.directory / artifact.filename).resolve()
            try:
                path.relative_to(self.directory)
            except ValueError as exc:
                self._remove_token(token)
                raise ArtifactNotFoundError("Generated audio metadata contained an invalid path.") from exc
            if not math.isfinite(artifact.expires_at):
                self._remove_token(token, filename=artifact.filename)
                raise ArtifactNotFoundError('Generated audio expiry metadata was invalid.')
            if artifact.expires_at <= timestamp:
                self._remove_token(token, filename=artifact.filename)
                raise ArtifactExpiredError(
                    "Generated audio link has expired. Generate the speech again with a new TTL."
                )
            if not path.is_file():
                self._remove_token(token)
                raise ArtifactNotFoundError("Generated audio file is missing. Generate the speech again.")
            return artifact, path

    def cleanup_expired(self, *, now: float | None = None) -> int:
        timestamp = datetime.now(tz=timezone.utc).timestamp() if now is None else now
        removed = 0
        with self._lock:
            for metadata_path in self.directory.glob("*.json"):
                try:
                    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
                    expires_at = float(payload["expires_at"])
                    filename = str(payload["filename"])
                    token = str(payload["token"])
                except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                    metadata_path.unlink(missing_ok=True)
                    removed += 1
                    continue
                if not token or len(token) != 43 or any(c not in _TOKEN_CHARACTERS for c in token):
                    metadata_path.unlink(missing_ok=True)
                    removed += 1
                    continue
                if metadata_path != self._metadata_path(token):
                    metadata_path.unlink(missing_ok=True)
                    removed += 1
                    continue
                if not math.isfinite(expires_at) or expires_at <= timestamp:
                    self._remove_token(token, filename=filename)
                    removed += 1
            for audio_path in self.directory.glob('qwen3tts-*.*'):
                token = audio_path.stem.removeprefix('qwen3tts-')
                if len(token) == 43 and all(c in _TOKEN_CHARACTERS for c in token) and not self._metadata_path(token).exists():
                    audio_path.unlink(missing_ok=True)
                    removed += 1
        return removed

    def _metadata_path(self, token: str) -> Path:
        if not token or any(c not in _TOKEN_CHARACTERS for c in token):
            raise ArtifactNotFoundError('Generated audio link was not found.')
        return self.directory / f"{token}.json"

    def _remove_token(self, token: str, *, filename: str | None = None) -> None:
        self._metadata_path(token).unlink(missing_ok=True)
        if filename:
            path = (self.directory / filename).resolve()
            try:
                path.relative_to(self.directory)
            except ValueError:
                return
            path.unlink(missing_ok=True)

    @staticmethod
    def _atomic_write(path: Path, content: bytes) -> None:
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)


_TOKEN_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
