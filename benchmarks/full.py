"""Full Faster Qwen product baseline with one resident checkpoint at a time."""
from __future__ import annotations

from copy import copy
import json
import re
import statistics
import time
import uuid

from .catalog import MODELS, payload
from .common import (GpuSampler, append_run, asr_inventory, backend_summary, container_memory,
    fingerprint, generate, gpu_snapshot, harness_metadata, image_metadata, judge, now_iso,
    percentile, request_json, safe_error, stable_seed, transcribe, version_metadata)
from .lifecycle import exclusive, isolated_gpu, wait_for_gpu_settle, worker
from .reports import render_baseline, render_streaming
from .run_baseline import register_reference, selected_workload, prepare_reference as bootstrap_reference
from .supplemental import evaluate_transcript, measure_queue, measure_ssml, render

SUITES = ('baseline', 'streaming', 'ssml', 'queue')


def full_plan(args, items):
    custom_count = sum(MODELS[model]['mode'] == 'custom' for model in args.models)
    return {'suite': 'full', 'engines': ['faster'], 'measured_models': args.models,
        'resident_models_per_profile': {model: [model] for model in args.models},
        'languages': list(dict.fromkeys(x['language'] for x in items)),
        'suites': {'baseline': len(items), 'streaming': len(items), 'ssml': custom_count * 2 * args.rounds,
            'queue': custom_count * 2 * args.rounds * args.clients},
        'measured_calls': 2 * len(items) + custom_count * 2 * args.rounds * (1 + args.clients),
        'warmup_calls_per_profile': args.warmup_calls, 'workload_sha256': fingerprint(items),
        'cohort_policy': 'one checkpoint at a time; load once, retain through its applicable suites, unload before the next checkpoint',
        'remote_asr_required': True, 'GPU_execution': False,
        'settings': {'temperature': .9, 'top_k': 50, 'repetition_penalty': 1.05,
            'max_new_tokens': args.max_new_tokens, 'chunk_size': args.chunk_size,
            'gpu_sample_seconds': args.sample_interval}}


def assert_resident(args):
    status = request_json('GET', args.base_url + '/tts/status')
    if set(status.get('resident_models', [])) != set(args.resident_models) or status.get('residency_errors') or status.get('error'):
        raise RuntimeError('Resident model cohort changed or failed; do not publish a controlled baseline.')
    return status


def assert_warm(metrics):
    if metrics.get('server_metrics', {}).get('model_load_ms') != 0:
        raise RuntimeError('A measured request loaded weights or omitted load telemetry.')


def load_cohort(args, hardware):
    # Use the same operator policy as the product, with optional nonresident workflows.
    defaults = {'custom': 'Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice',
        'clone': 'Qwen/Qwen3-TTS-12Hz-0.6B-Base', 'design': 'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign'}
    choices = {MODELS[model]['mode']: model for model in args.resident_models}
    policy = {'enabled': True, 'workflows': {mode: {'model': choices.get(mode, model), 'keep_loaded': False}
        for mode, model in defaults.items()}}
    request_json('PUT', args.base_url + '/system/settings', {'model_policy': policy}, timeout=900)
    stages = []
    with GpuSampler(args.gpu_index, args.sample_interval) as sampler:
        for model in args.resident_models:
            policy['workflows'][MODELS[model]['mode']]['keep_loaded'] = True
            started = time.perf_counter()
            request_json('PUT', args.base_url + '/system/settings', {'model_policy': policy}, timeout=900)
            stages.append({'model': model, 'seconds': time.perf_counter() - started,
                'status': request_json('GET', args.base_url + '/tts/status'), 'gpu': gpu_snapshot(args.gpu_index)})
            print('Loaded resident checkpoint ' + MODELS[model]['label'], flush=True)
    return {'stages': stages, 'seconds': sum(x['seconds'] for x in stages),
        'gpu': sampler.summary(hardware['used_mib']), 'status': assert_resident(args)}


def measure(args, model, delivery, items, voice, metadata):
    suffix = 'faster-' + MODELS[model]['label'] + '-' + delivery
    folder = args.artifacts / args.run_id / suffix; folder.mkdir(parents=True, exist_ok=True)
    before = assert_resident(args)
    def call(item, seed):
        options = payload(item, seed=seed, max_tokens=args.max_new_tokens, chunk_size=args.chunk_size)
        if MODELS[model]['mode'] == 'clone':
            options['voice_profile'] = voice
        return generate(args.base_url, options, streaming=delivery == 'streaming', request_id=str(uuid.uuid4()))
    warmups = []
    for index in range(args.warmup_calls):
        _, metrics = call(items[index % len(items)], 9001 + index)
        assert_warm(metrics); warmups.append(metrics)
    request_json('POST', args.base_url + '/benchmark/memory/reset', {})
    calls = []
    for index, item in enumerate(items, 1):
        record = {**item, 'seed': stable_seed(item['call_id'])}
        try:
            with GpuSampler(args.gpu_index, args.sample_interval) as sampler:
                audio, metrics = call(item, record['seed'])
            assert_warm(metrics)
            path = folder / (re.sub(r'[^a-zA-Z0-9_.-]', '_', item['call_id'].split('/')[-1]) + '.wav')
            path.write_bytes(audio)
            record.update(metrics, gpu=sampler.summary(metadata['gpu_baseline']['used_mib']),
                artifact=path.relative_to(args.artifacts).as_posix())
        except Exception as error:
            record.update(error_stage='tts', error=safe_error(error))
        calls.append(record)
        with (folder / 'calls.jsonl').open('a', encoding='utf-8') as journal:
            journal.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"[{suffix} {index}/{len(items)}] {item['call_id']}: {record.get('rtf', 'ERROR')}", flush=True)
    return {**metadata, 'model': model, 'revision': MODELS[model]['revision'], 'delivery': delivery,
        'warmups': warmups, 'calls': calls, 'status_before': before, 'status_after': assert_resident(args),
        'torch_memory': request_json('GET', args.base_url + '/benchmark/memory'),
        'container_memory': container_memory(args.active_container)}


def persist_stage(args, suite, profiles):
    folder = args.artifacts / args.run_id; folder.mkdir(parents=True, exist_ok=True)
    (folder / (suite + '-tts.json')).write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run_full(args):
    items = selected_workload(args)
    if args.plan:
        print(json.dumps(full_plan(args, items), ensure_ascii=False, indent=2)); return 0
    if not args.asr_url.startswith(('http://', 'https://')):
        raise ValueError('Configure the existing remote ASR service.')
    asr = asr_inventory(args.asr_url)
    items = selected_workload(args, asr['supported_languages'])
    config = full_plan(args, items)
    config['GPU_execution'] = True
    image = image_metadata(args.faster_image)
    groups = {suite: [] for suite in SUITES}
    started = now_iso(); loading = {}; teardown = {}; final_status = {}
    folder = args.artifacts / args.run_id; folder.mkdir(parents=True, exist_ok=True)
    with isolated_gpu(args):
        hardware = gpu_snapshot(args.gpu_index)
        if hardware is None:
            raise RuntimeError('NVIDIA telemetry is required.')
        hardware = wait_for_gpu_settle(args.gpu_index, hardware['used_mib'] + 128, 90, args.allow_shared_gpu)
        if any(x['mode'] == 'clone' for x in items):
            audio, reference = bootstrap_reference(args, args.faster_image)
            (folder / 'reference.wav').write_bytes(audio)
        else:
            audio, reference = b'', {'sha256': None, 'text': '', 'source': 'not used'}
        for model in args.models:
            current = copy(args); current.resident_models = [model]
            wait_for_gpu_settle(args.gpu_index, hardware['used_mib'] + 128, 90, args.allow_shared_gpu)
            with worker(current, 'faster', args.faster_image, 'full-' + MODELS[model]['label']) as (container, ready, info):
                measure_model(current, model, hardware, image, container, ready, info, audio, reference,
                    groups, loading, teardown, final_status, items)
            wait_for_gpu_settle(args.gpu_index, hardware['used_mib'] + 128, 90, args.allow_shared_gpu)
    # Judge after every TTS suite, with no ASR overlap in measurement windows.
    first = next((x for profiles in groups.values() for p in profiles for x in p.get('calls', []) if x.get('artifact')), None)
    if first:
        transcribe(args.asr_url, (args.artifacts / first['artifact']).read_bytes(), first['asr_language'], 'warmup')
    for suite in ['baseline', 'streaming', 'ssml']:
        for profile in groups[suite]:
            for call in profile['calls']:
                if call.get('error'):
                    continue
                try:
                    call.update(judge(args.asr_url, (args.artifacts / call['artifact']).read_bytes(), call))
                    if suite == 'ssml':
                        call.update(evaluate_transcript(call['transcript'], args.minimum_similarity))
                except Exception as error:
                    call.update(error_stage='asr', error=safe_error(error))
            if suite == 'ssml':
                profile['passed'] = all(x.get('passed', False) for x in profile['calls'])
            else:
                profile['summary'] = backend_summary(profile['calls'])
                ttfa = [x['client_ttfa_ms'] for x in profile['calls'] if x.get('client_ttfa_ms') is not None]
                profile['ttfa_median_ms'] = statistics.median(ttfa) if ttfa else None
                profile['ttfa_p95_ms'] = percentile(ttfa, .95) if ttfa else None
        persist_stage(args, suite, groups[suite])
        print('Completed remote judging for ' + suite, flush=True)
    run = {'schema': 1, 'run_id': args.run_id, 'suite': 'full', 'started_at': started, 'finished_at': now_iso(),
        'comment': args.comment, 'preliminary': args.no_write, 'hardware': hardware, 'asr': asr,
        'config': config, 'host_harness': harness_metadata(), 'workload_sha256': config['workload_sha256'],
        'reference': reference, 'loading': loading, 'teardown': teardown, 'resident_status_after_tests': final_status,
        'clients': args.clients, 'rounds': args.rounds, 'profiles': groups,
        'settings': config['settings']}
    (folder / 'run.json').write_text(json.dumps(run, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not args.no_write:
        for suite in SUITES:
            if not groups[suite]:
                continue
            specific = {**run, 'suite': suite, 'full_run_id': args.run_id, 'profiles': groups[suite], 'comparisons': []}
            suite_args = copy(args); suite_args.suite = suite
            path = args.artifacts / (suite + '-results') / 'runs.json'
            with exclusive(path.with_suffix('.json.lock')):
                data = append_run(path, specific)
                if suite == 'baseline':
                    render_baseline(data, args.reports)
                elif suite == 'streaming':
                    render_streaming(data, args.reports)
                else:
                    render(data, suite_args)
        with exclusive(args.results.with_suffix('.json.lock')):
            append_run(args.results, run)
    errors = sum(p['summary']['overall']['errors'] for suite in ['baseline', 'streaming'] for p in groups[suite])
    failed = errors or any(not p['passed'] for suite in ['ssml', 'queue'] for p in groups[suite])
    print(f"Completed full baseline: {config['measured_calls']} requests; evidence {folder / 'run.json'}", flush=True)
    return int(bool(failed))


def measure_model(args, model, hardware, image, container, ready, info, audio, reference,
                  groups, loading, teardown, final_status, workload):
    """One checkpoint owns this worker across all of its applicable suites."""
    if info.get('inference_workers') != 1:
        raise RuntimeError('Resident baseline requires one inference worker.')
    for model in args.resident_models:
        if info['models'][model]['revision'] != MODELS[model]['revision']:
            raise ValueError('Resident checkpoint revision differs from the catalog.')
    loading[model] = load_cohort(args, hardware)
    resident_idle = gpu_snapshot(args.gpu_index)
    voice = register_reference(args.base_url, audio, reference['text']) if MODELS[model]['mode'] == 'clone' else None
    metadata = {'engine': 'faster', 'incremental_waveforms': True, 'image': image,
        'worker_harness': info.get('harness'), 'runtime_versions': version_metadata(container),
        'api_ready_seconds': ready, 'resident_models': args.resident_models,
        'gpu_baseline': hardware, 'resident_idle_gpu': resident_idle,
        'cold_load_seconds': loading[model]['seconds'], 'cold_load_gpu': loading[model]['gpu'],
        'cold_load_scope': 'single measured checkpoint, retained through its suites'}
    for suite, delivery in [('baseline', 'complete'), ('streaming', 'streaming')]:
        items = [x for x in workload if x['model'] == model]
        groups[suite].append(measure(args, model, delivery, items, voice, metadata))
        persist_stage(args, suite, groups[suite])
    for suite in (['ssml', 'queue'] if MODELS[model]['mode'] == 'custom' else []):
        before = assert_resident(args)
        request_json('POST', args.base_url + '/benchmark/memory/reset', {})
        with GpuSampler(args.gpu_index, args.sample_interval) as sampler:
            profile = (measure_ssml(args, model, 'faster-' + MODELS[model]['label'] + '-' + suite, directed=MODELS[model]['instructions'])
                if suite == 'ssml' else measure_queue(args, model, 'faster-' + MODELS[model]['label'] + '-' + suite))
        calls = profile['calls'] if suite == 'ssml' else [x for batches in profile['batches'].values() for batch in batches for x in batch['calls']]
        for call in profile['warmups'] + calls:
            if not call.get('error'):
                assert_warm(call)
        groups[suite].append({**metadata, **profile, 'model': model, 'revision': MODELS[model]['revision'],
            'gpu': sampler.summary(hardware['used_mib']), 'status_before': before, 'status_after': assert_resident(args),
            'torch_memory': request_json('GET', args.base_url + '/benchmark/memory'),
            'container_memory': container_memory(container)})
        persist_stage(args, suite, groups[suite])
        print('Completed TTS suite ' + suite, flush=True)
    final_status[model] = assert_resident(args)
    before_unload = gpu_snapshot(args.gpu_index)
    with GpuSampler(args.gpu_index, args.sample_interval) as sampler:
        clock = time.perf_counter()
        unloaded = request_json('POST', args.base_url + '/studio/models/unload', {}, timeout=180)
        unload_seconds = time.perf_counter() - clock
    teardown[model] = {'seconds': unload_seconds, 'status': unloaded, 'gpu_before': before_unload,
        'gpu': sampler.summary(hardware['used_mib']), 'gpu_after': gpu_snapshot(args.gpu_index)}
