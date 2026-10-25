"""Measure preserved runtime images with continuously replenished HTTP clients."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from benchmarks.catalog import model_ids
from benchmarks.common import (ARTIFACTS_ROOT, GpuSampler, container_memory, generate,
    gpu_snapshot, harness_metadata, image_metadata, now_iso, request_json, version_metadata)
from benchmarks.lifecycle import isolated_gpu, wait_for_gpu_settle, worker
from benchmarks.supplemental import queue_payload
from benchmarks.sustained import measure


def render(run):
    lines = ['# Sustained concurrent inference', '',
        f"GPU: {run['hardware']['name']}, {run['hardware']['total_mib']} MiB; driver {run['hardware']['driver']}.", '',
        f"Checkpoint: `{run['model']}`. {run['seconds']:g}-second steady windows, "
        f"{run['passes']} passes at each client count and workload. Image order reverses "
        'on the second pass. Each client immediately replaces its completed request. '
        'A completed cycle of clients fills the queue before timing starts; the final '
        'drain is excluded from throughput. Each worker discards a seed-9001 warmup, '
        'then checks the seed-42 golden recording across images. Every load-test '
        'response, including fill and drain, must match that golden. '
        'All measured weights remain resident.', '',
        'Plain uses the existing paragraph. Processed uses two SSML turns with '
        'rate/pitch/volume, a 120 ms pause and whole-recording normalization. '
        'Each workload repeats one fixed seed (42), so audio duration and request '
        'content remain identical across clients, passes and images. This isolates '
        'scheduling; it is not a diverse production-traffic simulation.', '',
        'Sampling: temperature 0.9, top-k 50, repetition penalty 1.05, token cap 600, '
        'codec chunk size 8, complete WAV responses. GPU sampling requested every '
        '0.25 seconds; queue sampling every 0.05 seconds. Client occupancy is integrated '
        'from actual send/receive transitions. Queue depth is time-weighted from '
        'timestamped status samples. Latencies describe requests completing inside '
        'the steady window, including their queue wait. Complete-response latency '
        'is not a streaming first-audio measurement.', '',
        '| Workload | Clients | Before req/s | After req/s | Throughput change | Pass change range | Completed before / after |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for workload in run['workloads']:
        for clients in run['clients']:
            grouped = {stage: [p for p in run['profiles'] if p['stage'] == stage and
                p['workload'] == workload and p['clients'] == clients] for stage in ['before', 'after']}
            if any(len(items) != run['passes'] for items in grouped.values()):
                continue
            rates = {stage: sum(p['completed_in_window'] for p in items) / sum(p['seconds'] for p in items)
                for stage, items in grouped.items()}
            totals = {stage: sum(p['completed_in_window'] for p in items) for stage, items in grouped.items()}
            change = 100 * (rates['after'] / rates['before'] - 1)
            paired = {stage: {p['pass']: p['requests_per_second'] for p in items}
                for stage, items in grouped.items()}
            pass_changes = [100 * (paired['after'][number] / paired['before'][number] - 1)
                for number in paired['before']]
            lines.append(f"| {workload} | {clients} | {rates['before']:.4f} | {rates['after']:.4f} | "
                f"{change:+.2f}% | {min(pass_changes):+.2f}% to {max(pass_changes):+.2f}% | "
                f"{totals['before']} / {totals['after']} |")
    lines += ['', 'Completed-request counts have finite-window boundary variation. '
        'Pass results below show repeatability; two passes do not establish statistical '
        'confidence or a universal speedup. Keep the burst benchmark as a separate workload.', '',
        '| Pass | Image | Workload | Clients | Req/s | Mean outstanding | Mean waiting | Median latency s | p95 latency s | Mean GPU use % | Peak VRAM MiB | Valid |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for p in run['profiles']:
        q = p['queue']['mean_queued']
        lines.append(f"| {p['pass']} | {p['stage']} | {p['workload']} | {p['clients']} | "
            f"{p['requests_per_second']:.4f} | {p['mean_outstanding_clients']:.3f} | "
            f"{q:.3f} | {p['latency_median_seconds']:.3f} | {p['latency_p95_seconds']:.3f} | "
            f"{p['gpu']['mean_utilization_percent']} | {p['gpu']['peak_mib']} | {p['passed']} |")
    lines += ['', 'GPU use and peak VRAM include the Windows desktop. GPU telemetry covers '
        'fill and drain as well as the steady window. The status GPU-lease counter '
        'measures ownership, not CUDA kernel activity. Older runtimes omit the total '
        'synthesis-inflight counter; client occupancy remains available for both images.', '',
        f"Run: `{run['run_id']}`; harness `{run['harness']['sha256']}`; driver `{run['driver_sha256']}`.", '',
        '## Preserved images', '']
    for stage, metadata in run['images'].items():
        lines += [f"- {stage}: `{metadata['id']}`"]
    for item in run['workers']:
        lines += ['', f"Pass {item['pass']} {item['stage']} inference hash: "
            f"`{item['runtime']['inference_source_sha256']}`."]
    lines += ['', 'No other inference service is stopped. Model cache is mounted read-only '
        'in temporary workers, and the original Studio container is restored after the run.', '']
    return '\n'.join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before-image', required=True)
    parser.add_argument('--after-image', required=True)
    parser.add_argument('--model', default='0.6B-CustomVoice')
    parser.add_argument('--clients', default='4,8')
    parser.add_argument('--workloads', default='plain,processed')
    parser.add_argument('--seconds', type=float, default=90)
    parser.add_argument('--passes', type=int, default=2)
    parser.add_argument('--port', type=int, default=8812)
    parser.add_argument('--gpu-index', type=int, default=0)
    parser.add_argument('--cache-volume', default='faster_qwen3_tts_studio_data')
    parser.add_argument('--stop-container', action='append', default=[])
    parser.add_argument('--output', type=Path, default=ROOT / 'benchmarks/inference_queue/SUSTAINED.md')
    parser.add_argument('--artifacts', type=Path, default=ARTIFACTS_ROOT)
    parser.add_argument('--no-write', action='store_true')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args(argv)
    try:
        args.clients = list(dict.fromkeys(int(v) for v in args.clients.split(',')))
        args.workloads = list(dict.fromkeys(args.workloads.split(',')))
        if not args.clients or any(v < 2 or v > 8 for v in args.clients):
            raise ValueError('Clients must be between 2 and 8, within default queue capacity.')
        if not args.workloads or set(args.workloads) - {'plain', 'processed'}:
            raise ValueError('Workloads must be plain and/or processed.')
        if not 1 <= args.seconds <= 3600 or not 1 <= args.passes <= 10:
            raise ValueError('Use 1 to 3600 seconds and 1 to 10 passes.')
        args.model = model_ids(args.model)[0]
        if not args.model.endswith('CustomVoice'):
            raise ValueError('This workload requires a CustomVoice checkpoint.')
    except ValueError as exc:
        parser.error(str(exc))
    args.base_url = f'http://127.0.0.1:{args.port}'
    args.container = 'qwen3_tts_sustained'
    args.run_id = time.strftime('%Y%m%d-%H%M%S', time.gmtime()) + '-' + uuid.uuid4().hex[:8]
    return args


def main(argv=None):
    args = parse_args(argv)
    if args.plan:
        print(json.dumps({'GPU_execution': False, 'clients': args.clients, 'seconds': args.seconds,
            'passes': args.passes, 'workloads': args.workloads,
            'steady_seconds': len(args.clients) * len(args.workloads) * args.passes * 2 * args.seconds,
            'policy': 'continuous replacement; fill and drain excluded; reversed image order'}, indent=2))
        return 0
    images = {'before': image_metadata(args.before_image), 'after': image_metadata(args.after_image)}
    run = {'schema': 1, 'run_id': args.run_id, 'started_at': now_iso(), 'profiles': [], 'workers': [],
        'model': args.model, 'clients': args.clients, 'workloads': args.workloads,
        'seconds': args.seconds, 'passes': args.passes, 'images': images,
        'harness': harness_metadata(), 'driver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    folder = args.artifacts / args.run_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'sustained.json'
    def checkpoint():
        path.write_text(json.dumps(run, indent=2) + '\n', encoding='utf-8')
    goldens, package_versions = {}, None
    with isolated_gpu(args):
        hardware = gpu_snapshot(args.gpu_index)
        if hardware is None:
            raise RuntimeError('GPU telemetry is required.')
        run['hardware'] = hardware
        for number in range(1, args.passes + 1):
            order = ['before', 'after'] if number % 2 else ['after', 'before']
            for stage in order:
                for attempt in range(3):
                    try:
                        wait_for_gpu_settle(args.gpu_index, hardware['used_mib'] + 128)
                        break
                    except RuntimeError:
                        if attempt == 2:
                            raise
                        print('Idle guard did not settle; retrying before measurements.', flush=True)
                image = args.before_image if stage == 'before' else args.after_image
                suffix = f'p{number}-{stage}'
                with worker(args, 'faster', image, suffix) as (container, ready, info):
                    if info['harness']['sha256'] != run['harness']['sha256']:
                        raise ValueError('Worker and host benchmark harness differ.')
                    runtime = version_metadata(container)
                    if package_versions is not None and runtime['packages'] != package_versions:
                        raise ValueError('Runtime dependency versions differ.')
                    package_versions = runtime['packages']
                    run['workers'].append({'pass': number, 'stage': stage, 'runtime': runtime,
                        'api_ready_seconds': ready})
                    request_json('POST', args.base_url + '/studio/models/load', {'model': args.model}, timeout=900)
                    for workload in args.workloads:
                        for seed in [9001, 42]:
                            _, metrics = generate(args.base_url, queue_payload(args.model, seed, workload=workload))
                            if seed == 42:
                                if workload in goldens and metrics['sha256'] != goldens[workload]:
                                    raise ValueError('Fixed-seed golden changed across runtime images.')
                                goldens[workload] = metrics['sha256']
                    run['goldens'] = dict(goldens)
                    checkpoint()
                    combinations = [(workload, clients) for workload in args.workloads for clients in args.clients]
                    if number % 2 == 0:
                        combinations.reverse()
                    for workload, clients in combinations:
                        print(f'Start pass {number} {stage} {workload} clients={clients}', flush=True)
                        with GpuSampler(args.gpu_index, .25) as sampler:
                            profile = measure(args.base_url, args.model, clients, args.seconds, workload, goldens[workload])
                        profile.update({'stage': stage, 'pass': number,
                            'gpu': sampler.summary(hardware['used_mib']), 'memory': container_memory(container)})
                        run['profiles'].append(profile)
                        checkpoint()
                        print(f"Done {suffix} {workload} c{clients}: {profile['requests_per_second']:.4f} req/s, "
                            f"mean clients={profile['mean_outstanding_clients']:.3f}, "
                            f"mean waiting={profile['queue']['mean_queued']:.3f}, pass={profile['passed']}", flush=True)
                        if not profile['passed']:
                            raise RuntimeError('Sustained profile failed qualification.')
    run['finished_at'], run['goldens'] = now_iso(), goldens
    checkpoint()
    if not args.no_write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render(run), encoding='utf-8')
    print('Sustained evidence:', args.run_id, flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
