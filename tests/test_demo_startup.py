"""Exercise local startup without a Hub account or model downloads."""
import os
from pathlib import Path
import subprocess
import sys


def test_local_demo_starts_without_huggingface_login(tmp_path):
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment.pop("HF_TOKEN", None)
    environment.update({
        "HF_HOME": str(tmp_path / "huggingface"),
        "HF_HUB_OFFLINE": "1",
        "DEMO_REQUIRE_LOGIN": "0",
        "DEMO_WEB_ONLY": "0",
        "DEMO_DEFAULT_BACKEND": "torch",
        "DEMO_AVAILABLE_BACKENDS": "torch",
        "DEMO_ENABLE_REFERENCE_PRESETS": "0",
        "ASSET_DIR": str(tmp_path / "assets"),
        "USAGE_BUCKET_MOUNT_PATH": str(tmp_path),
    })
    result = subprocess.run(
        [sys.executable, "-c", """
import runpy
import sys
from fastapi.testclient import TestClient
sys.path.insert(0, 'demo')
app = runpy.run_path('demo/server.py', run_name='startup_test')['app']
assert '/oauth/huggingface/login' not in {route.path for route in app.routes}
with TestClient(app) as client:
    status = client.get('/status')
    assert status.status_code == 200, status.text
    assert status.json()['available_backends'] == ['torch']
    assert status.json()['loaded'] is False
    assert client.get('/').status_code == 200
"""],
        cwd=root, env=environment, capture_output=True, text=True, timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr
