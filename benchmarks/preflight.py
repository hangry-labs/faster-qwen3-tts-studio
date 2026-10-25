"""Inspect pinned cached assets without importing Torch, loading a model or using a GPU."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from .catalog import MODELS, model_ids


def inventory(snapshot, *, hash_files=False):
    snapshot = Path(snapshot)
    for name in ['config.json', 'README.md', 'speech_tokenizer/config.json']:
        if not (snapshot / name).is_file():
            raise ValueError(f'Checkpoint is missing {name}.')
    if not list(snapshot.glob('*.safetensors')) or not list((snapshot / 'speech_tokenizer').glob('*.safetensors')):
        raise ValueError('Checkpoint is missing model or speech-tokenizer weights.')
    files = []
    for path in sorted(snapshot.rglob('*')):
        if not path.is_file():
            continue
        resolved = path.resolve()
        if not resolved.is_relative_to(snapshot.parent.parent.resolve()):
            raise ValueError('Cached asset points outside its checkpoint repository.')
        item = {'path': path.relative_to(snapshot).as_posix(), 'bytes': path.stat().st_size,
            'cached_object': resolved.name if re.fullmatch(r'[a-f0-9]{40,64}', resolved.name) else None}
        if hash_files:
            with path.open('rb') as file:
                item['sha256'] = hashlib.file_digest(file, 'sha256').hexdigest()
        files.append(item)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', default='all')
    parser.add_argument('--hash-files', action='store_true', help='Read and SHA-256 every cached file, including weights.')
    args = parser.parse_args(argv)
    from huggingface_hub import snapshot_download
    checkpoints = []
    for model in model_ids(args.models):
        spec = MODELS[model]
        snapshot = snapshot_download(model, revision=spec['revision'], local_files_only=True)
        checkpoints.append({'model': model, 'revision': spec['revision'], 'files': inventory(snapshot, hash_files=args.hash_files)})
    print(json.dumps({'GPU_execution': False, 'checkpoints': checkpoints}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
