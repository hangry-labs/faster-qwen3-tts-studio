"""Paired SSML reliability and FIFO throughput from the VoxCPMTTS methodology."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.sax.saxutils import escape
from collections import defaultdict
import difflib
import hashlib
import json
import statistics
import threading
import time
import unicodedata
import uuid

from .catalog import ROOT, MODELS, payload
from .common import (GpuSampler, append_run, asr_inventory, container_memory, generate,
    gpu_snapshot, harness_metadata, image_metadata, judge, now_iso, percentile, request_json, safe_error,
    stable_seed, transcribe, version_metadata)
from .lifecycle import exclusive, isolated_gpu, wait_for_gpu_settle, worker
from .reports import cell, metric, table, write

DIALOGUE = json.loads((ROOT / 'benchmarks/ssml/dialogue.json').read_text(encoding='utf-8'))
DIALOGUE_TURNS = DIALOGUE['DIALOGUE_TURNS']
TURN_ENDINGS = DIALOGUE['TURN_ENDINGS']
EXPECTED_TEXT = ' '.join(DIALOGUE_TURNS)
QUEUE_TEXT = ('A dependable local voice service should preserve its tone and timing while several applications '
    'submit work at once, even though one GPU worker performs each inference in order.')


def normalize_text(text):
    value = unicodedata.normalize('NFKC', text).casefold()
    return ' '.join(''.join(character if unicodedata.category(character)[0] in {'L', 'N'} else ' ' for character in value).split())


def evaluate_transcript(transcript, minimum_similarity=95.):
    actual, expected = normalize_text(transcript), normalize_text(EXPECTED_TEXT)
    endings = [normalize_text(value) for value in TURN_ENDINGS]
    hits = [ending in actual for ending in endings]
    cursor, ordered = 0, 0
    for ending in endings:
        index = actual.find(ending, cursor)
        if index >= 0:
            ordered += 1; cursor = index + len(ending)
    similarity = round(100 * difflib.SequenceMatcher(None, expected, actual).ratio(), 2)
    tail = actual.endswith(endings[-1])
    return {'exact': actual == expected, 'similarity_percent': similarity,
        'turn_endings_detected': sum(hits), 'ordered_turn_endings': ordered,
        'missing_turn_endings': [value for value, hit in zip(TURN_ENDINGS, hits) if not hit],
        'tail_complete': tail, 'passed': similarity >= minimum_similarity and all(hits) and ordered == len(endings) and tail}


def documents(directed=True):
    result = {}
    for kind in ['ssml', 'ssml-h']:
        body = []
        for index, text in enumerate(DIALOGUE_TURNS):
            voice = 'Ryan' if index % 2 == 0 else 'Aiden'
            direction = ''
            if kind == 'ssml-h' and directed:
                direction = ' h:direction="' + ('Curious and conversational' if index % 2 == 0 else 'Calm and clear') + '"'
            body.append(f'<voice name="{voice}"{direction}>{escape(text)}</voice>')
        result[kind] = '<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:h="https://hangrylabs.app/ns/ssml-h/1.0" xml:lang="en-US">\n' + '\n'.join(body) + '\n</speak>'
    return result


def seeds_for_rounds(rounds):
    return [DIALOGUE['FIXED_SEEDS'][index % len(DIALOGUE['FIXED_SEEDS'])] for index in range(rounds)]


class QueueMonitor:
    def __init__(self, url, interval=.02):
        self.url, self.interval = url, interval
        self.samples, self.errors = [], []
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def run(self):
        while not self.stop.is_set():
            try:
                status = request_json('GET', self.url + '/tts/status', timeout=3)
                self.samples.append({'active': int(status['state'] == 'generating'), 'queued': status['queue_depth']})
            except Exception as error:
                self.errors.append(safe_error(error))
            self.stop.wait(self.interval)

    def __enter__(self):
        self.thread.start(); return self

    def __exit__(self, *_):
        self.stop.set(); self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise RuntimeError('Queue monitor did not stop.')

    def summary(self):
        return {'samples': len(self.samples), 'errors': len(self.errors),
            'peak_active': max((item['active'] for item in self.samples), default=0),
            'peak_queued': max((item['queued'] for item in self.samples), default=0)}


def run_batch(url, model, call_ids, mode, *, generator=generate, max_tokens=600, chunk_size=8):
    barrier = threading.Barrier(len(call_ids)) if mode == 'queued' else None
    def submit(call_id):
        item = {'model': model, 'mode': 'custom', 'language': 'English', 'text': QUEUE_TEXT}
        options = payload(item, seed=stable_seed(call_id), max_tokens=max_tokens, chunk_size=chunk_size)
        if barrier:
            barrier.wait(timeout=30)
        audio, metrics = generator(url, options, request_id=str(uuid.uuid4()))
        return {'call_id': call_id, **metrics}, audio
    started = time.perf_counter()
    with QueueMonitor(url) as monitor:
        if mode == 'queued':
            with ThreadPoolExecutor(max_workers=len(call_ids)) as executor:
                results = list(executor.map(submit, call_ids))
        elif mode == 'sequential':
            results = [submit(call_id) for call_id in call_ids]
        else:
            raise ValueError('Expected sequential or queued submission.')
    return {'mode': mode, 'batch_wall_seconds': time.perf_counter() - started,
        'calls': [item[0] for item in results], 'audio': {item[0]['call_id']: item[1] for item in results},
        'queue': monitor.summary()}


def summarize_batches(batches):
    calls = [call for batch in batches for call in batch['calls']]
    total = sum(batch['batch_wall_seconds'] for batch in batches)
    times = [call['tts_seconds'] for call in calls]
    return {'calls': len(calls), 'rounds': len(batches), 'total_batch_wall_seconds': total,
        'request_latency_median_seconds': statistics.median(times), 'request_latency_p95_seconds': percentile(times, .95),
        'requests_per_second': len(calls) / total,
        'aggregate_realtime_speed': sum(call['audio_seconds'] for call in calls) / total,
        'peak_queued': max(batch['queue']['peak_queued'] for batch in batches),
        'peak_active': max(batch['queue']['peak_active'] for batch in batches),
        'monitor_errors': sum(batch['queue']['errors'] for batch in batches)}


def measure_queue(args, model, suffix):
    item = {'model': model, 'mode': 'custom', 'language': 'English', 'text': QUEUE_TEXT}
    warmups = [generate(args.base_url, payload(item, seed=9001 + index, max_tokens=args.max_new_tokens,
        chunk_size=args.chunk_size))[1] for index in range(args.warmup_calls)]
    batches = {'sequential': [], 'queued': []}
    matching, compared = 0, 0
    for number in range(1, args.rounds + 1):
        call_ids = [f'round-{number:02d}-client-{index:02d}' for index in range(1, args.clients + 1)]
        paired = {}
        for mode in (['sequential', 'queued'] if number % 2 else ['queued', 'sequential']):
            paired[mode] = run_batch(args.base_url, model, call_ids, mode,
                max_tokens=args.max_new_tokens, chunk_size=args.chunk_size)
        for call_id in call_ids:
            compared += 1
            matching += paired['sequential']['audio'][call_id] == paired['queued']['audio'][call_id]
        mismatched = any(paired['sequential']['audio'][key] != paired['queued']['audio'][key] for key in call_ids)
        for mode, batch in paired.items():
            if mismatched:
                for call_id, audio in batch['audio'].items():
                    folder = args.artifacts / args.run_id / suffix
                    folder.mkdir(parents=True, exist_ok=True)
                    (folder / f'{mode}-{call_id}.wav').write_bytes(audio)
            batch.pop('audio'); batches[mode].append(batch)
    sequential, queued = (summarize_batches(batches[mode]) for mode in ['sequential', 'queued'])
    return {'warmups': warmups, 'batches': batches, 'sequential': sequential, 'queued': queued,
        'comparison': {'compared_outputs': compared, 'matching_outputs': matching,
            'throughput_change_percent': 100 * (queued['requests_per_second'] / sequential['requests_per_second'] - 1)},
        'passed': matching == compared and queued['peak_queued'] >= 1 and queued['peak_active'] <= 1 and not queued['monitor_errors']}


def measure_ssml(args, model, suffix, *, directed=True):
    cases, warmups = [], []
    for kind, document in documents(directed).items():
        item = {'model': model, 'mode': 'custom', 'language': 'English', 'text': document}
        options = payload(item, seed=9001, max_tokens=args.max_new_tokens, chunk_size=args.chunk_size); options['input_type'] = kind
        for index in range(args.warmup_calls):
            _, metrics = generate(args.base_url, {**options, 'seed': 9001 + index})
            warmups.append({'scenario': kind, **metrics})
        for number, seed in enumerate(seeds_for_rounds(args.rounds), 1):
            record = {'scenario': kind, 'round': number, 'seed': seed,
                'call_id': f'{kind}-r{number:02d}', 'language': 'English', 'asr_language': 'English', 'text': EXPECTED_TEXT}
            try:
                audio, metrics = generate(args.base_url, {**options, 'seed': seed})
                folder = args.artifacts / args.run_id / suffix; folder.mkdir(parents=True, exist_ok=True)
                path = folder / (record['call_id'] + '.wav'); path.write_bytes(audio)
                record.update(metrics, artifact=path.relative_to(args.artifacts).as_posix())
            except Exception as error:
                record.update(error=safe_error(error), error_stage='tts')
            cases.append(record)
    return {'warmups': warmups, 'calls': cases, 'documents': documents(directed), 'delivery_directions': directed}


def render(data, args):
    lines = ['# ' + ('SSML dialogue reliability' if args.suite == 'ssml' else 'Inference queue throughput'), '']
    rows = []
    for run in data['runs']:
        for profile in run['profiles']:
            identity = [run['run_id'], profile['engine'], MODELS[profile['model']]['label']]
            if args.suite == 'ssml':
                for scenario in ['ssml', 'ssml-h']:
                    calls = [call for call in profile['calls'] if call['scenario'] == scenario]
                    judged = [call for call in calls if 'similarity_percent' in call]
                    rows.append(identity + [scenario, sum(call.get('passed', False) for call in calls), len(calls),
                        sum(call.get('tail_complete', False) for call in calls),
                        metric(statistics.fmean(call['similarity_percent'] for call in judged), 2) if judged else 'n/a',
                        metric(statistics.median(call['rtf'] for call in judged)) if judged else 'n/a'])
            else:
                comparison = profile['comparison']
                rows.append(identity + [run['clients'], run['rounds'], metric(profile['sequential']['total_batch_wall_seconds']),
                    metric(profile['queued']['total_batch_wall_seconds']), metric(comparison['throughput_change_percent'], 2),
                    f"{comparison['matching_outputs']}/{comparison['compared_outputs']}", profile['queued']['peak_queued'], profile['passed']])
    headers = ['Run', 'Engine', 'Checkpoint'] + (['Input', 'Passed', 'Rounds', 'Complete tails', 'Mean similarity %', 'Median RTF']
        if args.suite == 'ssml' else ['Clients', 'Rounds', 'Sequential s', 'Queued s', 'Throughput change %', 'Identical WAVs', 'Peak queue', 'Pass'])
    note = ('The same ten turns and final-tail checks as VoxCPMTTS; fixed Ryan/Aiden voices. Delivery directions are used only on capable checkpoints; each profile records this scope. ASR is a comparative judge.'
        if args.suite == 'ssml' else 'One GPU worker; alternate batch order each round. Queued latency includes waiting time. A throughput change is not a claim that FIFO accelerates model inference.')
    write(args.reports / ('ssml' if args.suite == 'ssml' else 'inference_queue') / 'BENCHMARKS.md', lines + [note, '', *table(headers, rows), ''])
    details = ['# ' + args.suite + ' details', '', 'Latest run: ' + data['latest']['run_id'], '']
    for profile in data['latest']['profiles']:
        details += ['## ' + profile['engine'] + ' / ' + MODELS[profile['model']]['label'], '',
            f"Image `{profile['image']['id']}`; source `{profile['runtime_versions']['inference_source_sha256']}`.", '']
        if args.suite == 'ssml':
            details += table(['Input', 'Round', 'Seed', 'Pass', 'Tail', 'Endings', 'Ordered', 'Similarity %',
                'TTS s', 'Audio s', 'RTF', 'ASR s', 'Transcript', 'WAV SHA-256'], [
                [call['scenario'], call['round'], call['seed'], call.get('passed', False), call.get('tail_complete', False),
                    call.get('turn_endings_detected', 0), call.get('ordered_turn_endings', 0), call.get('similarity_percent', 'n/a'),
                    call.get('tts_seconds', 'n/a'), call.get('audio_seconds', 'n/a'), call.get('rtf', 'n/a'),
                    call.get('asr_seconds', 'n/a'), call.get('transcript', call.get('error_stage', '')), call.get('sha256', 'n/a')]
                for call in profile['calls']]) + ['']
        else:
            details += table(['Submission', 'Round', 'Batch wall s', 'Peak active', 'Peak queued'], [
                [mode, index, metric(batch['batch_wall_seconds']), batch['queue']['peak_active'], batch['queue']['peak_queued']]
                for mode, batches in profile['batches'].items() for index, batch in enumerate(batches, 1)]) + ['']
    write(args.reports / ('ssml' if args.suite == 'ssml' else 'inference_queue') / 'DETAILS.md', details)


def run_supplemental(args):
    for model in args.models:
        if MODELS[model]['mode'] != 'custom' or (args.suite == 'ssml' and not MODELS[model]['instructions']):
            raise ValueError('SSML requires 1.7B CustomVoice; queue tests require a CustomVoice checkpoint.')
    if args.plan:
        print(json.dumps({'suite': args.suite, 'engines': args.backends, 'models': args.models,
            'rounds': args.rounds, 'clients': args.clients if args.suite == 'queue' else 1,
            'calls_per_profile': args.rounds * (2 if args.suite == 'ssml' else 2 * args.clients),
            'remote_asr_required': args.suite == 'ssml', 'GPU_execution': False}, indent=2))
        return 0
    asr = None
    if args.suite == 'ssml':
        if not args.asr_url.startswith(('http://', 'https://')):
            raise ValueError('Configure the existing remote ASR service.')
        asr = asr_inventory(args.asr_url)
        if 'English' not in asr['supported_languages']:
            raise ValueError('The judge must support English.')
    started = now_iso(); profiles = []
    images = {'native': args.native_image, 'faster': args.faster_image}
    for engine in args.backends:
        image_metadata(images[engine])
    with isolated_gpu(args):
        hardware = gpu_snapshot(args.gpu_index)
        if hardware is None:
            raise RuntimeError('NVIDIA telemetry is required.')
        for engine in args.backends:
            for model in args.models:
                wait_for_gpu_settle(args.gpu_index, hardware['used_mib'] + 128, 90, args.allow_shared_gpu)
                suffix = engine + '-' + MODELS[model]['label'] + '-' + args.suite
                with worker(args, engine, images[engine], suffix) as (container, ready, info):
                    if info['models'][model]['revision'] != MODELS[model]['revision']:
                        raise ValueError('Candidate checkpoint revision differs.')
                    if args.suite == 'queue' and info.get('inference_workers', 1) != 1:
                        raise ValueError('Queue benchmark requires one inference worker.')
                    request_json('POST', args.base_url + '/studio/models/load', {'model': model}, timeout=900)
                    with GpuSampler(args.gpu_index, args.sample_interval) as sampler:
                        profile = measure_ssml(args, model, suffix) if args.suite == 'ssml' else measure_queue(args, model, suffix)
                    profiles.append({**profile, 'engine': engine, 'model': model, 'image': image_metadata(images[engine]),
                        'runtime_versions': version_metadata(container), 'gpu': sampler.summary(hardware['used_mib']),
                        'worker_harness': info.get('harness'),
                        'container_memory': container_memory(container), 'api_ready_seconds': ready})
    if args.suite == 'ssml':
        first = next((call for profile in profiles for call in profile['calls'] if call.get('artifact')), None)
        if first:
            try:
                transcribe(args.asr_url, (args.artifacts / first['artifact']).read_bytes(), 'English', 'warmup')
            except Exception as error:
                asr['warmup_error'] = safe_error(error)
        for profile in profiles:
            for call in profile['calls']:
                if call.get('error'):
                    continue
                try:
                    call.update(judge(args.asr_url, (args.artifacts / call['artifact']).read_bytes(), call))
                    call.update(evaluate_transcript(call['transcript'], args.minimum_similarity))
                except Exception as error:
                    call.update(error=safe_error(error), error_stage='asr')
            profile['passed'] = all(call.get('passed', False) for call in profile['calls'])
    run = {'schema': 1, 'run_id': args.run_id, 'suite': args.suite, 'started_at': started, 'finished_at': now_iso(),
        'comment': args.comment, 'preliminary': args.no_write, 'shared_gpu': args.allow_shared_gpu,
        'hardware': hardware, 'asr': asr, 'clients': args.clients,
        'rounds': args.rounds, 'host_harness': harness_metadata(), 'settings': {'max_new_tokens': args.max_new_tokens, 'chunk_size': args.chunk_size, 'temperature': .9, 'top_k': 50,
            'repetition_penalty': 1.05, 'warmup_calls': args.warmup_calls}, 'profiles': profiles}
    path = args.artifacts / args.run_id / 'run.json'; path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(run, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not args.no_write:
        with exclusive(args.results.with_suffix('.json.lock')):
            render(append_run(args.results, run), args)
    return 0 if all(profile['passed'] for profile in profiles) else 1
