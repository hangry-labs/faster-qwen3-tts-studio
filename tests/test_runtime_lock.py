"""Supported runtime pins must be complete binary/hash inputs, not floating roots."""
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_lock_has_exact_versions_and_distribution_hashes():
    content = (ROOT / 'requirements.runtime.txt').read_text(encoding='utf-8')
    blocks = re.split(r'\n(?=[a-zA-Z0-9])', content)
    packages = {}
    for block in blocks:
        if block.startswith('--'):
            continue
        match = re.match(r'([A-Za-z0-9_.-]+)==([^\s\\]+)', block)
        assert match, block[:120]
        assert re.search(r'--hash=sha256:[a-f0-9]{64}(?:\s|$)', block), match[1]
        packages[match[1].lower().replace('_', '-')] = match[2]
    assert packages['torch'] == '2.10.0+cu128'
    assert packages['transformers'] == '5.15.1'
    assert packages['mcp'] == '2.3.0'
    assert {'pydantic', 'pydantic-core', 'nvidia-cublas-cu12', 'starlette', 'httpx2', 'python-stretch'} <= packages.keys()
    assert not any(marker in content for marker in ['.ai/', 'sandbox', 'file://', ' @ '])


def test_docker_installs_locked_wheels_without_floating_build_dependencies():
    dockerfile = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
    assert '--require-hashes -r requirements.runtime.txt' in dockerfile
    assert dockerfile.count('--no-build-isolation --no-deps') == 2
    assert 'QWEN_STUDIO_BUILD_ID=${VCS_REF}' in dockerfile
