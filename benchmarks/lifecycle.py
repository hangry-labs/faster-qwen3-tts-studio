"""Owned, isolated Docker workers. Never removes arbitrary named containers."""
from __future__ import annotations
from contextlib import contextmanager
import json
import time
import uuid
from pathlib import Path
from .common import ARTIFACTS_ROOT, docker, gpu_snapshot, request_json

OWNER_LABEL = 'app.hangrylabs.benchmark'
OWNER = 'faster-qwen3-tts-studio'


@contextmanager
def exclusive(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    try:
        with path.open('x', encoding='utf-8') as file:
            file.write(token)
    except FileExistsError as error:
        raise RuntimeError(f'Benchmark lock exists: {path.name}. Check for an active run before removing a stale lock.') from error
    try:
        yield
    finally:
        if path.exists() and path.read_text(encoding='utf-8') == token:
            path.unlink()


def inspect_container(name):
    result = docker('container', 'inspect', name, check=False, timeout=20)
    return json.loads(result.stdout)[0] if result.returncode == 0 else None


def remove_owned(name, token):
    current = inspect_container(name)
    if current is None:
        return
    labels = current.get('Config', {}).get('Labels', {})
    if labels.get(OWNER_LABEL) != OWNER or labels.get(OWNER_LABEL + '.run') != token:
        raise RuntimeError('Refusing to remove a container owned by another run.')
    docker('rm', '--force', name, timeout=45)


def wait_ready(url, timeout=180):
    started = time.monotonic()
    while time.monotonic() - started < timeout:
        try:
            if request_json('GET', url + '/tts/ping', timeout=3).get('msg') == 'pong':
                return round(time.monotonic() - started, 4)
        except (OSError, ValueError):
            pass
        time.sleep(.5)
    raise RuntimeError('Isolated benchmark API did not become ready.')


def wait_for_gpu_settle(index, maximum, timeout=90, allow_shared=False):
    deadline = time.monotonic() + timeout
    stable = 0
    while time.monotonic() < deadline:
        snapshot = gpu_snapshot(index)
        if snapshot is None:
            raise RuntimeError('NVIDIA telemetry is unavailable.')
        if allow_shared:
            return snapshot
        stable = stable + 1 if snapshot['used_mib'] <= maximum and snapshot['utilization_percent'] <= 5 else 0
        if stable >= 3:
            return snapshot
        time.sleep(1)
    raise RuntimeError('GPU did not return to the pre-run idle baseline. Check other workloads.')


@contextmanager
def worker(args, engine, image, suffix):
    token = uuid.uuid4().hex
    name = args.container + '-' + token[:8]
    if inspect_container(name) is not None:
        raise RuntimeError('Benchmark container name collision.')
    args.active_container = name
    started = False
    try:
        started = True
        docker('run', '--detach', '--init', '--name', name,
            '--label', OWNER_LABEL + '=' + OWNER, '--label', OWNER_LABEL + '.run=' + token,
            '--gpus', f'device={args.gpu_index}', '--publish', f'127.0.0.1:{args.port}:7860',
            '--mount', f'type=volume,source={args.cache_volume},target=/cache,readonly',
            '--env', 'HF_HOME=/cache/huggingface', '--env', 'HF_HUB_OFFLINE=1',
            '--env', 'TRANSFORMERS_OFFLINE=1', '--env', 'QWEN_STUDIO_DATA=/tmp/benchmark-studio',
            '--env', 'TORCHINDUCTOR_CACHE_DIR=/tmp/benchmark-inductor',
            '--env', 'TORCHINDUCTOR_COMPILE_THREADS=1', '--entrypoint', 'python', image,
            '-m', 'benchmarks.server', '--engine', engine, timeout=60)
        ready = wait_ready(args.base_url)
        info = request_json('GET', args.base_url + '/benchmark/info')
        if info['engine'] != engine:
            raise RuntimeError('Benchmark worker reported the wrong inference engine.')
        yield name, ready, info
    finally:
        if started:
            try:
                log = docker('logs', name, check=False, timeout=20)
                folder = args.artifacts / args.run_id / 'logs'
                folder.mkdir(parents=True, exist_ok=True)
                (folder / (suffix + '.log')).write_text(log.stdout + log.stderr, encoding='utf-8')
            finally:
                remove_owned(name, token)


@contextmanager
def isolated_gpu(args):
    with exclusive(ARTIFACTS_ROOT / f'gpu-{args.gpu_index}.lock'):
        docker('volume', 'inspect', args.cache_volume, timeout=20)
        stopped = []
        try:
            for name in dict.fromkeys(args.stop_container):
                current = inspect_container(name)
                if current and current.get('State', {}).get('Running'):
                    stopped.append(name)
                    docker('stop', '--time', '60', name, timeout=90)
            yield
        finally:
            for name in stopped:
                docker('start', name, check=False, timeout=60)
