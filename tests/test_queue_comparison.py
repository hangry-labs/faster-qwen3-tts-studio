from copy import deepcopy

import pytest

from scripts.compare_queue_runs import compare


def run(seconds=4):
    batch = {'batch_wall_seconds': seconds, 'calls': [
        {'call_id': name, 'seed': 42, 'sha256': 'audio', 'server_metrics': {'model_load_ms': 0}}
        for name in ['one', 'two']]}
    summary = {'request_latency_median_seconds': seconds, 'request_latency_p95_seconds': seconds}
    return {'suite': 'queue', 'shared_gpu': False, 'clients': 2, 'rounds': 1, 'settings': {},
        'hardware': dict(name='test', driver='test', total_mib=100), 'host_harness': {'sha256': 'same'},
        'run_id': str(seconds), 'profiles': [{'engine': 'faster', 'model': 'model', 'workload': 'plain', 'passed': True,
            'runtime_versions': {'packages': {}, 'inference_source_sha256': 'source'},
            'batches': {'sequential': [deepcopy(batch)], 'queued': [deepcopy(batch)]},
            'sequential': summary, 'queued': summary, 'image': {'id': 'image'},
            'gpu': {'peak_mib': 100}, 'container_memory': {'peak_mib': 200}}]}


def test_comparison_uses_same_submission_mode_and_before_after_wall_times():
    row, = compare(run(4), run(2))
    assert row['changes']['queued']['throughput_change_percent'] == 100
    assert row['changes']['sequential']['throughput_change_percent'] == 100


@pytest.mark.parametrize('change', ['audio', 'cold', 'harness', 'failed', 'shared', 'packages', 'clients'])
def test_comparison_refuses_unqualified_or_mismatched_results(change):
    before, after = run(), run()
    profile = after['profiles'][0]
    if change == 'audio':
        profile['batches']['queued'][0]['calls'][0]['sha256'] = 'changed'
    elif change == 'cold':
        profile['batches']['sequential'][0]['calls'][0]['server_metrics']['model_load_ms'] = 1
    elif change == 'harness':
        after['host_harness']['sha256'] = 'changed'
    elif change == 'failed':
        profile['passed'] = False
    elif change == 'shared':
        after['shared_gpu'] = True
    elif change == 'packages':
        profile['runtime_versions']['packages'] = {'torch': 'changed'}
    else:
        after['clients'] = 4
    with pytest.raises(ValueError):
        compare(before, after)
