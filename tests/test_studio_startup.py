"""Exercise the real Studio's fresh startup without accounts, network or models."""
import os
from pathlib import Path
import subprocess
import sys


def test_studio_starts_offline_without_inherited_recordings(tmp_path):
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    for key in ('HF_TOKEN', 'QWEN_STUDIO_ASR_URL'):
        environment.pop(key, None)
    environment.update({
        'HF_HOME': str(tmp_path / 'huggingface'),
        'HF_HUB_OFFLINE': '1',
        'QWEN_STUDIO_DATA': str(tmp_path / 'studio'),
    })
    result = subprocess.run(
        [sys.executable, '-c', """
import socket
from pathlib import Path
import os
from unittest.mock import patch

def no_network(*args, **kwargs):
    raise AssertionError('Studio startup must not download models or recordings')

with patch.object(socket.socket, 'connect', no_network), patch.object(socket.socket, 'connect_ex', no_network):
    from fastapi.testclient import TestClient
    from faster_qwen3_tts.standalone_ui.server import create_app
    app = create_app()
    assert not any(route.path.startswith('/oauth/') for route in app.routes)
    with TestClient(app) as client:
        status = client.get('/status').json()
        assert status['available_backends'] == ['torch']
        assert status['loaded'] is False
        assert client.get('/').status_code == 200
        assert client.get('/studio/voices').json() == {'voices': []}
        assert len(client.get('/studio/capabilities').json()['models']) == 5
    data = Path(os.environ['QWEN_STUDIO_DATA'])
    assert not list((data / 'voices').iterdir())
    assert not list(Path(os.environ['HF_HOME']).rglob('*.safetensors'))
"""],
        cwd=root, env=environment, capture_output=True, text=True, timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr
