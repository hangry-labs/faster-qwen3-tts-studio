"""Saved-script names cannot select paths outside their storage directory."""
import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location('dialogue_scripts',
    Path(__file__).parents[1] / 'src/faster_qwen3_tts/standalone_ui/dialogue_scripts.py')
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


@pytest.mark.parametrize('name', ['Normal script', '../../escape', r'..\..\escape', '/absolute/escape'])
def test_script_names_stay_inside_storage_and_preserve_document(tmp_path, name):
    root = tmp_path / 'scripts'
    outside = tmp_path / 'escape'
    outside.write_text('Keep this file', encoding='utf-8')
    document = '<speak xmlns="http://www.w3.org/2001/10/synthesis">A &amp; B</speak>'
    script_id, record = storage.save_dialogue_script(root, name=name, document=document)
    saved = root / record['document_file']
    assert saved.resolve().parent == root.resolve()
    assert saved.read_text(encoding='utf-8') == document + '\n'
    assert script_id in storage.load_dialogue_scripts(root)
    assert storage.resolve_dialogue_script(root, script_id)[2] == saved.resolve()
    assert outside.read_text(encoding='utf-8') == 'Keep this file'
    assert not list(root.glob('*.tmp'))


def test_download_rejects_external_document_paths_and_symlinks(tmp_path):
    root = tmp_path / 'scripts'
    outside = tmp_path / 'outside.ssml'
    outside.write_text('Private outside file', encoding='utf-8')
    script_id, record = storage.save_dialogue_script(root, name='Safe', document='<speak>Safe</speak>')
    index = root / 'scripts.json'
    original = index.read_text(encoding='utf-8')
    for filename in ['../outside.ssml', str(outside.resolve())]:
        payload = json.loads(original)
        payload[script_id]['document_file'] = filename
        index.write_text(json.dumps(payload), encoding='utf-8')
        with pytest.raises(ValueError, match='does not exist'):
            storage.resolve_dialogue_script(root, script_id)
    index.write_text(original, encoding='utf-8')
    document = root / record['document_file']
    document.unlink()
    try:
        document.symlink_to(outside)
    except OSError:
        pytest.skip('Creating symlinks is unavailable on this host')
    with pytest.raises(ValueError, match='does not exist'):
        storage.resolve_dialogue_script(root, script_id)
