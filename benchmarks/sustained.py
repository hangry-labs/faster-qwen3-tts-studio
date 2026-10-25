"""Closed-loop HTTP load with an explicit steady window and retained timelines."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import statistics
import threading
import time
import uuid

from .common import generate, percentile, request_json, safe_error
from .supplemental import queue_payload


def occupancy(events, start, end):
    """Exact time-weighted client occupancy, clipped to the steady window."""
    count, area, cursor, peak = 0, 0., start, 0
    for timestamp, delta in sorted(events):
        if timestamp <= start:
            count += delta
            continue
        if timestamp > end:
            break
        peak = max(peak, count)
        area += count * (timestamp - cursor)
        cursor = timestamp
        count += delta
    peak = max(peak, count)
    area += count * (end - cursor)
    return {'mean': area / (end - start), 'peak': peak}


def sampled_mean(samples, key, start, end):
    """Use actual sample times, with the previous observation carried forward."""
    area, covered = 0., 0.
    for index, item in enumerate(samples):
        left = max(start, item['time'])
        right = min(end, samples[index + 1]['time'] if index + 1 < len(samples) else end)
        if right > left and item.get(key) is not None:
            area += item[key] * (right - left)
            covered += right - left
    return area / covered if covered else None


class Monitor:
    def __init__(self, url, interval=.05):
        self.url, self.interval = url, interval
        self.samples, self.errors = [], []
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def run(self):
        while not self.stop.is_set():
            try:
                status = request_json('GET', self.url + '/tts/status', timeout=3)
                info = status.get('queue', {})
                self.samples.append({'time': time.perf_counter(),
                    'queued': status['queue_depth'],
                    'active': info.get('active', int(status['state'] == 'generating')),
                    'inflight': info.get('inflight')})
            except Exception as error:
                self.errors.append(safe_error(error))
            self.stop.wait(self.interval)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop.set()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise RuntimeError('Sustained queue monitor failed to stop.')


def measure(url, model, clients, seconds, workload, golden_sha256, *, generator=generate,
            monitor_factory=Monitor, clock=time.perf_counter, seed=42, max_tokens=600, chunk_size=8):
    if not 2 <= clients <= 8 or seconds <= 0:
        raise ValueError('Use 2 to 8 clients and a positive measurement duration.')
    lock, barrier, abort = threading.Lock(), threading.Barrier(clients), threading.Event()
    records, errors, transitions = [], [], []
    warm_completed, window_start = 0, None
    started = clock()
    options = queue_payload(model, seed, max_tokens, chunk_size, workload)

    def client(lane):
        nonlocal warm_completed, window_start
        barrier.wait(timeout=30)
        sequence = 0
        while not abort.is_set():
            with lock:
                sent = clock()
                if window_start is not None and sent >= window_start + seconds:
                    return
                # One completed cycle of all clients fills and warms the queue.
                if window_start is None and warm_completed >= clients:
                    window_start = sent
                transitions.append((sent, 1))
            sequence += 1
            try:
                _, metrics = generator(url, options.copy(), request_id=str(uuid.uuid4()))
                received = clock()
                if metrics['sha256'] != golden_sha256:
                    raise ValueError('Audio differs from the fixed-seed golden recording.')
                if metrics['server_metrics'].get('model_load_ms') != 0:
                    raise ValueError('A measured request loaded weights or omitted load telemetry.')
                with lock:
                    records.append({'lane': lane, 'sequence': sequence, 'sent': sent,
                        'received': received, **metrics})
            except Exception as error:
                received = clock()
                with lock:
                    errors.append(safe_error(error))
                abort.set()
            finally:
                with lock:
                    transitions.append((received, -1))
                    warm_completed += 1

    with monitor_factory(url) as monitor, ThreadPoolExecutor(max_workers=clients) as executor:
        list(executor.map(client, range(clients)))
    ended = clock()
    if errors:
        raise RuntimeError('Sustained load failed: ' + '; '.join(errors))
    if window_start is None:
        raise RuntimeError('The steady window did not start.')
    window_end = window_start + seconds
    completed = [item for item in records if window_start <= item['received'] < window_end]
    if not completed:
        raise RuntimeError('No request completed during the steady window.')
    requests = occupancy(transitions, window_start, window_end)
    queue = {'samples': len(monitor.samples), 'errors': monitor.errors,
        'mean_queued': sampled_mean(monitor.samples, 'queued', window_start, window_end),
        'mean_gpu_lease_active': sampled_mean(monitor.samples, 'active', window_start, window_end),
        'mean_server_inflight': sampled_mean(monitor.samples, 'inflight', window_start, window_end),
        'peak_gpu_leases': max((s['active'] for s in monitor.samples), default=0)}
    timings = [item['received'] - item['sent'] for item in completed]
    return {'clients': clients, 'workload': workload, 'seconds': seconds,
        'warm_completed_target': clients, 'fill_seconds': window_start - started,
        'drain_seconds': max(0, ended - window_end), 'golden_sha256': golden_sha256,
        'completed_in_window': len(completed), 'total_calls': len(records),
        'requests_per_second': len(completed) / seconds,
        'realtime_speed': sum(item['audio_seconds'] for item in completed) / seconds,
        'latency_median_seconds': statistics.median(timings),
        'latency_p95_seconds': percentile(timings, .95),
        'mean_outstanding_clients': requests['mean'], 'peak_outstanding_clients': requests['peak'],
        'queue': queue, 'calls': records,
        'window': {'start': window_start, 'end': window_end},
        'client_transitions': transitions, 'queue_samples': monitor.samples,
        'passed': not monitor.errors and queue['mean_queued'] is not None and queue['peak_gpu_leases'] <= 1 and
            requests['mean'] >= clients * .95}
