"""Closed-loop admission and measurement boundaries without a GPU."""
import json
import threading
import time

import pytest

from benchmarks.sustained import measure, occupancy, sampled_mean
from scripts import benchmark_sustained_queue as driver


def test_client_occupancy_clips_fill_and_drain_and_integrates_exactly():
    events = [(0, 1), (1, 1), (3, -1), (4, 1), (6, -1), (8, -1)]
    value = occupancy(events, 2, 7)
    assert value['peak'] == 2
    assert value['mean'] == pytest.approx((2 + 1 + 4 + 1) / 5)


def test_queue_mean_weights_actual_sample_intervals_and_carries_prior_value():
    samples = [{'time': 0, 'queued': 8}, {'time': 2, 'queued': 4}, {'time': 5, 'queued': 1}]
    assert sampled_mean(samples, 'queued', 1, 7) == pytest.approx((8 + 12 + 2) / 6)
    assert sampled_mean(samples, 'missing', 1, 7) is None


class Monitor:
    def __init__(self, url):
        self.samples = [{'time': time.perf_counter(), 'queued': 1, 'active': 1, 'inflight': 2}]
        self.errors = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


def test_load_replenishes_clients_and_excludes_fill_and_drain():
    lock, calls = threading.Lock(), []
    def generate(url, payload, **_):
        sent = time.perf_counter()
        time.sleep(.015)
        with lock:
            calls.append(sent)
        return b'wav', {'sha256': 'golden', 'audio_seconds': 1,
            'server_metrics': {'model_load_ms': 0}}
    value = measure('unused', 'model', 2, .08, 'plain', 'golden', generator=generate, monitor_factory=Monitor)
    assert value['passed']
    assert value['total_calls'] > 4
    assert value['fill_seconds'] > 0 and value['drain_seconds'] > 0
    assert value['mean_outstanding_clients'] > 1.9
    assert value['peak_outstanding_clients'] == 2
    start, end = value['window']['start'], value['window']['end']
    assert value['completed_in_window'] == sum(start <= c['received'] < end for c in value['calls'])
    assert value['total_calls'] > value['completed_in_window']
    assert all(c['sent'] < end for c in value['calls'])
    assert len({c['lane'] for c in value['calls']}) == 2


@pytest.mark.parametrize('bad', ['audio', 'load'])
def test_load_aborts_and_drains_on_mismatched_audio_or_cold_weights(bad):
    def generate(*args, **kwargs):
        return b'wav', {'sha256': 'wrong' if bad == 'audio' else 'golden',
            'audio_seconds': 1, 'server_metrics': {'model_load_ms': 1 if bad == 'load' else 0}}
    with pytest.raises(RuntimeError, match='Sustained load failed'):
        measure('unused', 'model', 2, .1, 'plain', 'golden', generator=generate, monitor_factory=Monitor)


def test_plan_does_not_touch_docker_network_or_gpu(monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        pytest.fail('Offline plan attempted external work')
    for name in ['image_metadata', 'gpu_snapshot', 'request_json', 'worker']:
        monkeypatch.setattr(driver, name, forbidden)
    assert driver.main(['--before-image', 'old', '--after-image', 'new', '--plan']) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan['GPU_execution'] is False
    assert plan['clients'] == [4, 8] and plan['steady_seconds'] == 16 * 90


@pytest.mark.parametrize('flags', [['--clients', '9'], ['--seconds', '0'], ['--passes', '0'],
    ['--workloads', 'bad'], ['--model', '0.6B-Base']])
def test_invalid_experiments_are_rejected_before_measurement(flags):
    with pytest.raises(SystemExit):
        driver.parse_args(['--before-image', 'old', '--after-image', 'new', *flags])


def test_report_aggregates_completed_requests_and_exposes_pass_variation():
    run = {'hardware': {'name': 'GPU', 'total_mib': 16, 'driver': 'test'},
        'model': 'model', 'seconds': 90, 'passes': 2, 'clients': [4], 'workloads': ['processed'],
        'run_id': 'test', 'harness': {'sha256': 'harness'}, 'driver_sha256': 'driver',
        'images': {}, 'workers': [], 'profiles': []}
    for stage, counts in [('before', [34, 38]), ('after', [41, 40])]:
        for number, count in enumerate(counts, 1):
            run['profiles'].append({'stage': stage, 'pass': number, 'clients': 4,
                'workload': 'processed', 'seconds': 90, 'completed_in_window': count,
                'requests_per_second': count / 90, 'mean_outstanding_clients': 4,
                'queue': {'mean_queued': 3}, 'latency_median_seconds': 1,
                'latency_p95_seconds': 1, 'gpu': {'mean_utilization_percent': 90, 'peak_mib': 1},
                'passed': True})
    report = driver.render(run)
    assert '+12.50%' in report  # Aggregate 81/72, rather than averaging percentages.
    assert '+5.26% to +20.59%' in report
    assert '72 / 81' in report
