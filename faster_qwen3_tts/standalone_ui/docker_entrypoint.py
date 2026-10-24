"""Merge baked checkpoints into the product cache, then start the Studio."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys
import tempfile


def seed_cache(source: Path, destination: Path) -> int:
    if not source.is_dir():
        return 0
    source = source.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    destination = destination.resolve()
    copied = 0
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        # Lock files are downloader state, not model assets.
        if '.locks' in relative.parts:
            continue
        target = destination / relative
        if not path.resolve().is_relative_to(source) or not target.resolve().is_relative_to(destination):
            raise ValueError(f'Cache symlink escapes its root: {relative}')
        if path.is_symlink():
            link = os.readlink(path)
            if target.is_symlink() and os.readlink(target) == link:
                continue
            if target.is_file() and not target.is_symlink() and target.stat().st_size == path.stat().st_size:
                continue
            if target.exists() or target.is_symlink():
                raise ValueError(f'Conflicting model-cache entry: {relative}')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(link)
        elif path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            if target.is_file() and target.stat().st_size == path.stat().st_size:
                # HF blobs are content-addressed; compare small mutable metadata.
                if 'blobs' in relative.parts or target.read_bytes() == path.read_bytes():
                    continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
                pending = Path(temporary.name)
            try:
                shutil.copyfile(path, pending)
                pending.replace(target)
            finally:
                pending.unlink(missing_ok=True)
            copied += 1
    return copied


def main():
    source = Path('/app/baked-models/huggingface')
    destination = Path(os.getenv('HF_HOME', '/app/persistent/huggingface'))
    copied = seed_cache(source, destination)
    if source.is_dir():
        print(f'[startup] Baked model cache ready ({copied} files copied).', flush=True)
    os.execv(sys.executable, [sys.executable, '-m', 'faster_qwen3_tts.standalone_ui.server'])


if __name__ == '__main__':
    main()
