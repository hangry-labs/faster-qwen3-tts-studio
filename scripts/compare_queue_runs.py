"""Render matched queue experiments without copying private run metadata."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics


def compare(before, after):
    if any(run['suite'] != 'queue' or run.get('shared_gpu') for run in [before, after]):
        raise ValueError('Comparison requires isolated queue runs.')
    for key in ['clients', 'rounds', 'settings']:
        if before[key] != after[key]:
            raise ValueError('Mismatched benchmark ' + key)
    for key in ['name', 'driver', 'total_mib']:
        if before['hardware'][key] != after['hardware'][key]:
            raise ValueError('Mismatched GPU ' + key)
    if before['host_harness']['sha256'] != after['host_harness']['sha256']:
        raise ValueError('Mismatched benchmark harness.')
    def profiles(run):
        values = {(p['engine'], p['model'], p.get('workload', 'plain')): p for p in run['profiles']}
        if len(values) != len(run['profiles']):
            raise ValueError('Duplicate checkpoint/workload profiles.')
        return values
    a, b = profiles(before), profiles(after)
    if a.keys() != b.keys():
        raise ValueError('Mismatched checkpoint/workload profiles.')
    rows = []
    for identity, old in a.items():
        new = b[identity]
        if not all(p['passed'] for p in [old, new]):
            raise ValueError('Cannot compare failed queue qualification.')
        if old['runtime_versions']['packages'] != new['runtime_versions']['packages']:
            raise ValueError('Mismatched runtime packages.')
        changes = {}
        for mode in ['sequential', 'queued']:
            old_batches, new_batches = old['batches'][mode], new['batches'][mode]
            if len(old_batches) != len(new_batches):
                raise ValueError('Mismatched measured rounds.')
            for first, second in zip(old_batches, new_batches):
                def calls(batch):
                    values = {c['call_id']: (c['seed'], c['sha256']) for c in batch['calls']}
                    if len(values) != before['clients'] or len(values) != len(batch['calls']):
                        raise ValueError('Incomplete or duplicate client results.')
                    return values
                if calls(first) != calls(second):
                    raise ValueError('Output identity changed across images.')
                if any(c['server_metrics']['model_load_ms'] != 0 for batch in [first, second] for c in batch['calls']):
                    raise ValueError('Measured requests must use resident weights.')
            old_time = sum(x['batch_wall_seconds'] for x in old_batches)
            new_time = sum(x['batch_wall_seconds'] for x in new_batches)
            changes[mode] = {'before_seconds': old_time, 'after_seconds': new_time,
                'throughput_change_percent': 100 * (old_time / new_time - 1),
                'latency_median_before': old[mode]['request_latency_median_seconds'],
                'latency_median_after': new[mode]['request_latency_median_seconds'],
                'latency_p95_before': old[mode]['request_latency_p95_seconds'],
                'latency_p95_after': new[mode]['request_latency_p95_seconds'],
                'round_changes_percent': [100 * (x['batch_wall_seconds'] / y['batch_wall_seconds'] - 1)
                    for x, y in zip(old_batches, new_batches)]}
        def mean_metric(profile, key):
            values = [c['server_metrics'][key] for batch in profile['batches']['queued'] for c in batch['calls']
                if key in c['server_metrics']]
            return statistics.fmean(values) if values else None
        rows.append({'engine': identity[0], 'model': identity[1], 'workload': identity[2],
            'before_run': before['run_id'], 'after_run': after['run_id'],
            'identical_outputs': before['rounds'] * before['clients'], 'changes': changes,
            'before_image': old['image']['id'], 'after_image': new['image']['id'],
            'before_source': old['runtime_versions']['inference_source_sha256'],
            'after_source': new['runtime_versions']['inference_source_sha256'],
            'before_gpu_peak_mib': old['gpu']['peak_mib'], 'after_gpu_peak_mib': new['gpu']['peak_mib'],
            'before_ram_peak_mib': old['container_memory']['peak_mib'],
            'after_ram_peak_mib': new['container_memory']['peak_mib'],
            'after_mean_gpu_lease_ms': mean_metric(new, 'gpu_lease_ms'),
            'after_mean_postprocess_ms': mean_metric(new, 'postprocess_ms')})
    return rows


def render(rows, hardware, settings, clients, rounds):
    lines = ['# Concurrent processing experiment', '',
        f"GPU: {hardware['name']} ({hardware['total_mib']} MiB), driver {hardware['driver']}.", '',
        f'{clients} concurrent clients, {rounds} paired rounds per workload and image. '
        'Sequential and queued order alternates each round; fixed seeds and WAV output. '
        'Each isolated worker loads one checkpoint and discards its warmup. '
        'All measured model-load times are zero. Other containers remain untouched.', '',
        f"Sampling: temperature {settings['temperature']}, top-k {settings['top_k']}, "
        f"repetition penalty {settings['repetition_penalty']}, token cap {settings['max_new_tokens']}, "
        f"chunk size {settings['chunk_size']}. GPU telemetry requested every 0.1 s.", '',
        'Plain is the existing speech control. Processed is two SSML turns with rate/pitch/volume '
        'effects, a 120 ms break and whole-recording loudness normalization. '
        'Gains below compare the same submission mode across images. '
        'They do not compare sequential submission against queued submission. '
        'Before/after labels denote code versions; run IDs show execution order. '
        'Repeating the baseline image after the candidate helps check drift.', '',
        '| Workload | Submission | Before s | After s | Throughput change | Round change range |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
    for row in rows:
        for mode, value in row['changes'].items():
            ranges = value['round_changes_percent']
            lines.append(f"| {row['workload']} | {mode} | {value['before_seconds']:.3f} | "
                f"{value['after_seconds']:.3f} | {value['throughput_change_percent']:+.2f}% | "
                f"{min(ranges):+.2f}% to {max(ranges):+.2f}% |")
    lines += ['', 'Round ranges show observed variation, not confidence intervals. '
        'These are short complete-response workloads on one GPU; results do not establish '
        'a general speedup for every text, checkpoint, clone reference or streaming format. '
        'VRAM figures include the variable desktop baseline. RAM is the container high-water mark, '
        'including file-cache accounting. These figures do not establish an allocator-memory improvement.', '',
        '| Workload | Queued median latency before / after s | Queued p95 before / after s | GPU peak before / after MiB | RAM peak before / after MiB | Identical WAVs per mode |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for row in rows:
        value = row['changes']['queued']
        lines.append(f"| {row['workload']} | {value['latency_median_before']:.3f} / {value['latency_median_after']:.3f} | "
            f"{value['latency_p95_before']:.3f} / {value['latency_p95_after']:.3f} | "
            f"{row['before_gpu_peak_mib']} / {row['after_gpu_peak_mib']} | "
            f"{row['before_ram_peak_mib']} / {row['after_ram_peak_mib']} | {row['identical_outputs']} |")
    for row in rows:
        lease = row['after_mean_gpu_lease_ms']
        tail = row['after_mean_postprocess_ms']
        lease_text = 'unavailable' if lease is None else f'{lease:.3f} ms'
        tail_text = 'unavailable' if tail is None else f'{tail:.3f} ms'
        lines += ['', f"## {row['workload']}: {row['model']}", '',
            f"Before run `{row['before_run']}`; after run `{row['after_run']}`.", '',
            f"Before image `{row['before_image']}`; after image `{row['after_image']}`.", '',
            f"Inference source hashes: `{row['before_source']}` and `{row['after_source']}`.", '',
            f"After: mean queued GPU lease {lease_text}; mean CPU tail {tail_text}. "
            'The lease includes model-side preparation, inference and codec decoding. '
            'The CPU tail can overlap the next request; HTTP encoding is measured only by client latency.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, action='append', required=True)
    parser.add_argument('--after', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, default=Path('benchmarks/inference_queue/PROCESSING.md'))
    args = parser.parse_args()
    if len(args.before) != len(args.after):
        parser.error('Supply the same number of paired before and after files.')
    rows = []
    for a, b in zip(args.before, args.after):
        before, after = (json.loads(path.read_text(encoding='utf-8')) for path in [a, b])
        rows.extend(compare(before, after))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(rows, before['hardware'], before['settings'], before['clients'], before['rounds']), encoding='utf-8')
    print('Compared identical fixed-seed outputs and wrote', args.output)


if __name__ == '__main__':
    main()
