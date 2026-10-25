"""Explicit bounded reference locations for native APIs and advanced MCP."""
from __future__ import annotations

import asyncio
import io
import os
from pathlib import Path

from fastapi import UploadFile

from .remote_audio import RemoteAudioFetcher

MAX_REFERENCE_BYTES = 10 * 1024 * 1024


class ReferenceInputs:
    def __init__(self, root: Path, *, fetcher=None):
        self.root = Path(os.getenv('QWEN_STUDIO_MCP_INPUT_DIR', str(root))).resolve()
        self.fetcher = fetcher or RemoteAudioFetcher(max_bytes=MAX_REFERENCE_BYTES,
            allowed_hosts=os.getenv('QWEN_STUDIO_AUDIO_URL_ALLOWED_HOSTS', '*').split(','), timeout_seconds=30)

    async def read(self, location: str, *, allow_url=True) -> UploadFile:
        if not isinstance(location, str) or not location.strip() or len(location) > 2048:
            raise ValueError('Provide a reference audio location up to 2048 characters.')
        if location.startswith(('http://', 'https://')):
            if not allow_url:
                raise ValueError('This endpoint accepts container-local references only. Use an upload for remote audio.')
            downloaded = await self.fetcher.fetch(location)
            return UploadFile(io.BytesIO(downloaded.payload), filename=downloaded.filename)

        def read_local():
            candidate = (self.root / location).resolve()
            if not candidate.is_relative_to(self.root) or candidate == self.root:
                raise ValueError('Reference paths must stay inside the configured MCP input directory.')
            if not candidate.is_file():
                raise ValueError('Choose a regular audio file inside the configured input directory.')
            try:
                with candidate.open('rb') as handle:
                    content = handle.read(MAX_REFERENCE_BYTES + 1)
            except OSError as exc:
                raise ValueError('Reference audio was not found in the configured input directory.') from exc
            if not content or len(content) > MAX_REFERENCE_BYTES:
                raise ValueError('Reference audio must be non-empty and at most 10 MB.')
            return content, candidate.name

        content, filename = await asyncio.to_thread(read_local)
        return UploadFile(io.BytesIO(content), filename=filename)
