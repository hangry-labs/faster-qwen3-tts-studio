"""Browser-origin checks prevent cross-site writes without requiring API cookies."""
from fastapi.testclient import TestClient
import pytest

from faster_qwen3_tts.standalone_ui.runtime import StudioEngine
from faster_qwen3_tts.standalone_ui.server import browser_write_allowed, create_app


@pytest.mark.parametrize('origin', ['https://untrusted.invalid', 'null', '', 'http://[',
    'http://testserver:90', 'http://testserver@untrusted.invalid', 'http://testserver/path'])
def test_cross_site_browser_post_cannot_unload_models(tmp_path, origin):
    engine = StudioEngine()
    calls = []
    engine.unload = lambda: calls.append('unload') or {'unloaded': True}
    with TestClient(create_app(engine, tmp_path)) as client:
        response = client.post('/studio/models/unload', headers={'Origin': origin})
    assert response.status_code == 403
    assert not calls


@pytest.mark.parametrize('origin', [None, 'http://testserver', 'http://testserver:80', 'https://testserver'])
def test_same_host_browser_and_ordinary_api_clients_keep_working(tmp_path, origin):
    engine = StudioEngine()
    calls = []
    engine.unload = lambda: calls.append('unload') or {'unloaded': True}
    with TestClient(create_app(engine, tmp_path)) as client:
        response = client.post('/studio/models/unload', headers={'Origin': origin} if origin is not None else {})
    assert response.status_code == 200
    assert calls == ['unload']


def test_foreign_browser_write_keeps_openai_error_shape(tmp_path, monkeypatch):
    monkeypatch.delenv('QWEN_STUDIO_API_KEY', raising=False)
    with TestClient(create_app(StudioEngine(), tmp_path)) as client:
        response = client.post('/v1/audio/voices', headers={'Origin': 'https://untrusted.invalid'})
    assert response.status_code == 403
    assert response.json()['error']['type'] == 'invalid_request_error'
    assert response.headers['Cache-Control'] == 'no-store'


def test_origin_authority_comparison_handles_ipv6_and_invalid_ports():
    assert browser_write_allowed('http://[::1]:7860', '[::1]:7860')
    assert not browser_write_allowed('http://[::1]:7860', '[::1]:7861')
    assert not browser_write_allowed('https://testserver:bad', 'testserver')
