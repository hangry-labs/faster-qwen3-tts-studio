"""Fetch all five pinned Studio checkpoints, including their upstream cards."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import runpy

from huggingface_hub import snapshot_download

# Read the shared stdlib-only catalog without importing the inference package.
# The asset stage needs Hub downloads, not Torch/model initialization.
MODELS = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                           'faster_qwen3_tts/standalone_ui/model_catalog.py'))['MODELS']


def prefetch(cache_root: Path, *, offline: bool = False) -> list[dict]:
    records = []
    for spec in MODELS.values():
        snapshot = Path(snapshot_download(spec['id'], revision=spec['revision'],
                        cache_dir=str(cache_root / 'hub'), local_files_only=offline))
        if not (snapshot / 'README.md').is_file() or not (snapshot / 'config.json').is_file():
            raise RuntimeError(f"Checkpoint lacks its model card or configuration: {spec['id']}")
        if not any(snapshot.rglob('*.safetensors')):
            raise RuntimeError(f"Checkpoint has no weights: {spec['id']}")
        if not (snapshot / 'speech_tokenizer/config.json').is_file():
            raise RuntimeError(f"Checkpoint has no embedded speech tokenizer: {spec['id']}")
        files = []
        for path in sorted(snapshot.rglob('*')):
            if path.is_file():
                with path.open('rb') as stream:
                    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                files.append({'path': path.relative_to(snapshot).as_posix(),
                              'bytes': path.stat().st_size, 'sha256': digest})
        records.append({'id': spec['id'], 'revision': spec['revision'],
                        'license': spec['license'], 'files': files})
        print(f"Verified {spec['id']} at {spec['revision']}", flush=True)
    cache_root.mkdir(parents=True, exist_ok=True)
    (cache_root / 'model-manifest.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-root', type=Path, required=True)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    prefetch(args.cache_root, offline=args.offline)


if __name__ == '__main__':
    main()
