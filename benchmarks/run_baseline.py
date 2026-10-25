"""Controlled multilingual baseline, adapted from VoxCPMTTS (Apache-2.0).

Manual only. --plan performs no Docker, network or GPU operations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import statistics
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from benchmarks.catalog import (MODELS, CORPUS_PATH, REFERENCE_TEXT, REFERENCE_INSTRUCTION,
    model_ids, workload, payload)
from benchmarks.common import (ARTIFACTS_ROOT, GpuSampler, append_run, asr_inventory, backend_summary,
    container_memory, fingerprint, generate, gpu_snapshot, harness_metadata, image_metadata, judge, multipart, now_iso,
    request_json, safe_error, stable_seed, transcribe, version_metadata, wav_duration)
from benchmarks.lifecycle import exclusive, isolated_gpu, wait_for_gpu_settle, worker
from benchmarks.reports import render_baseline, compare_profiles, render_pilot, render_streaming
import urllib.request


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-image', default='faster-qwen3-tts-studio:benchmark')
    parser.add_argument('--faster-image', default='faster-qwen3-tts-studio:benchmark')
    parser.add_argument('--backends', default='faster')
    parser.add_argument('--models')
    parser.add_argument('--modes', default='custom,design,clone')
    parser.add_argument('--delivery', choices=['complete', 'streaming', 'both'], default='complete')
    parser.add_argument('--container', default='qwen3_tts_benchmark')
    parser.add_argument('--port', type=int, default=8812)
    parser.add_argument('--gpu-index', type=int, default=0)
    parser.add_argument('--cache-volume', default='faster_qwen3_tts_studio_data')
    parser.add_argument('--reference-audio', type=Path)
    parser.add_argument('--reference-text', default='')
    parser.add_argument('--manifest', type=Path, default=CORPUS_PATH)
    parser.add_argument('--asr-url', default=os.getenv('QWEN_BENCHMARK_ASR_URL') or os.getenv('QWEN_STUDIO_ASR_URL', ''))
    parser.add_argument('--design-sentences', type=int, default=2)
    parser.add_argument('--repeats', '--calls', type=int, default=5)
    parser.add_argument('--clone-repeats', type=int)
    parser.add_argument('--warmup-calls', type=int)
    parser.add_argument('--languages', default='')
    parser.add_argument('--sample-interval', type=float, default=.1)
    parser.add_argument('--max-new-tokens', type=int, default=600)
    parser.add_argument('--chunk-size', type=int, default=8)
    parser.add_argument('--results', type=Path)
    parser.add_argument('--reports', type=Path, default=ROOT / 'benchmarks')
    parser.add_argument('--artifacts', type=Path, default=ARTIFACTS_ROOT)
    parser.add_argument('--stop-container', action='append', default=[])
    parser.add_argument('--comment', default='')
    parser.add_argument('--suite', choices=['baseline', 'backends', 'streaming', 'ssml', 'queue', 'full'], default='baseline')
    parser.add_argument('--rounds', type=int, default=5)
    parser.add_argument('--clients', type=int, default=4)
    parser.add_argument('--queue-workload', choices=['plain', 'processed'], default='plain',
        help='Queue control or two-turn SSML with prosody and whole-recording normalization.')
    parser.add_argument('--minimum-similarity', type=float, default=95.)
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--no-write', action='store_true', help='Retain local evidence, but do not append history or update reports.')
    parser.add_argument('--allow-shared-gpu', action='store_true', help='Preliminary smoke only: record contention without requiring an idle GPU.')
    args = parser.parse_args(argv)
    try:
        if args.allow_shared_gpu and not args.no_write:
            raise ValueError('Shared-GPU smoke requires --no-write; it cannot publish benchmark history.')
        defaults = {'ssml': '1.7B-CustomVoice', 'queue': '0.6B-CustomVoice',
            'backends': '0.6B-CustomVoice,0.6B-Base,1.7B-VoiceDesign'}
        args.models = model_ids(args.models or defaults.get(args.suite, '0.6B-CustomVoice,0.6B-Base'))
        if args.clone_repeats is None:
            args.clone_repeats = args.repeats if args.suite == 'backends' else 3
        if args.warmup_calls is None:
            args.warmup_calls = 2 if args.suite == 'backends' else 1
        args.backends = list(dict.fromkeys(name.strip() for name in args.backends.split(',') if name.strip()))
        if not args.backends or set(args.backends) - {'native', 'faster'}:
            raise ValueError('Backends must be native, faster, or native,faster.')
        if args.suite == 'full':
            if args.backends != ['faster']:
                raise ValueError('The full product baseline measures Faster Qwen only.')
        args.modes = args.modes.split(',')
        if set(args.modes) - {'custom', 'design', 'clone'}:
            raise ValueError('Unknown mode filter.')
        if args.suite == 'full':
            args.models = [model for model in args.models if MODELS[model]['mode'] in args.modes]
            if not args.models:
                raise ValueError('No checkpoint matches the full suite workflow filter.')
        if min(args.repeats, args.design_sentences, args.warmup_calls, args.rounds) < 1 or args.clone_repeats < 0:
            raise ValueError('Counts and warmups must be positive; clone repeats may be zero.')
        if not 0 < args.sample_interval <= 10 or not 24 <= args.max_new_tokens <= 600 or not 1 <= args.chunk_size <= 64:
            raise ValueError('Invalid sampling interval, token cap or chunk size.')
        if not 1 <= args.port <= 65535 or args.gpu_index < 0 or not 2 <= args.clients <= 32:
            raise ValueError('Invalid port, GPU index or client count (2 to 32).')
        if any(not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]*', value) for value in [args.container, args.cache_volume]):
            raise ValueError('Use simple Docker container and volume names.')
        if not 0 <= args.minimum_similarity <= 100:
            raise ValueError('Similarity must be from 0 to 100.')
        if bool(args.reference_audio) != bool(args.reference_text.strip()):
            raise ValueError('Supply both --reference-audio and its exact --reference-text, or neither.')
        if args.reference_audio and not args.reference_audio.is_file():
            raise ValueError('Reference audio does not exist.')
        if args.reference_audio and args.reference_audio.stat().st_size > 10 * 1024 * 1024:
            raise ValueError('Reference audio must be no larger than 10 MB.')
        if len(args.reference_text) > 4000:
            raise ValueError('Reference transcript must fit the 4000-character API limit.')
        if args.suite == 'streaming':
            args.delivery = 'streaming'
    except ValueError as error:
        parser.error(str(error))
    args.results = args.results or args.artifacts / (args.suite + '-results') / 'runs.json'
    args.base_url = f'http://127.0.0.1:{args.port}'
    args.run_id = time.strftime('%Y%m%d-%H%M%S', time.gmtime()) + '-' + uuid.uuid4().hex[:8]
    args.asr_url = args.asr_url.rstrip('/')
    return args


def selected_workload(args, supported=None):
    items = workload(args.models, languages=args.languages, supported=supported,
        design_sentences=args.design_sentences, repeats=args.repeats, clone_repeats=args.clone_repeats,
        modes=args.modes, corpus_path=args.manifest)
    if args.suite == 'backends':
        # Compact four-scenario diagnostic, covering built-in, design, another
        # supported language and cloning. Keep repeats for each chosen case.
        wanted = []
        for mode, language in [('custom', 'English'), ('design', 'English'), ('design', 'Japanese'), ('clone', 'English')]:
            candidate = next((item for item in items if item['mode'] == mode and item['language'] == language), None)
            if candidate:
                wanted.append(candidate['case_id'])
        items = [item for item in items if item['case_id'] in wanted]
        if not items:
            raise ValueError('Pilot filters removed all four diagnostic scenarios.')
    return items


def plan(args, items):
    deliveries = ['complete', 'streaming'] if args.delivery == 'both' else [args.delivery]
    return {'suite': args.suite, 'models': list(dict.fromkeys(item['model'] for item in items)),
        'languages': list(dict.fromkeys(item['language'] for item in items)), 'engines': args.backends,
        'deliveries': deliveries, 'measured_calls_per_engine': len(items) * len(deliveries),
        'profiles': [{'engine': engine, 'model': model, 'delivery': delivery,
            'calls': sum(item['model'] == model for item in items)}
            for engine in args.backends for model in dict.fromkeys(item['model'] for item in items) for delivery in deliveries],
        'workload_sha256': fingerprint(items), 'reference': ('provided recording' if args.reference_audio else 'fixed synthetic voice, generated once before measurement') if any(item['mode'] == 'clone' for item in items) else 'not used',
        'remote_asr_required': True, 'GPU_execution': False, 'shared_gpu': args.allow_shared_gpu,
        'settings': {'temperature': .9, 'top_k': 50, 'repetition_penalty': 1.05,
            'max_new_tokens': args.max_new_tokens, 'chunk_size': args.chunk_size,
            'warmup_calls_per_profile': args.warmup_calls, 'gpu_sample_seconds': args.sample_interval}}


def register_reference(url, content, text):
    body, content_type = multipart({'name': 'benchmark-reference', 'ref_text': text, 'language': 'English'},
        {'reference_audio': ('reference.wav', content)})
    with urllib.request.urlopen(urllib.request.Request(url + '/tts/voice-profiles', data=body,
        headers={'Content-Type': content_type}), timeout=60) as response:
        result = json.load(response)
    return result['id']


def prepare_reference(args, image):
    if args.reference_audio:
        content = args.reference_audio.read_bytes()
        return content, {'sha256': hashlib.sha256(content).hexdigest(), 'text': args.reference_text,
            'source': 'operator-provided authorized reference', 'bytes': len(content)}
    design = next(model for model, spec in MODELS.items() if spec['mode'] == 'design')
    with worker(args, 'faster', image, 'reference-bootstrap'):
        item = {'model': design, 'mode': 'design', 'language': 'English', 'text': REFERENCE_TEXT, 'instruct': REFERENCE_INSTRUCTION}
        content, metrics = generate(args.base_url, payload(item, seed=42, max_tokens=args.max_new_tokens))
    folder = args.artifacts / args.run_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'reference.wav').write_bytes(content)
    return content, {'sha256': metrics['sha256'], 'text': REFERENCE_TEXT, 'instruction': REFERENCE_INSTRUCTION,
        'source': 'synthetic VoiceDesign bootstrap, excluded from timings', 'model': design,
        'revision': MODELS[design]['revision'], 'seed': 42, 'bytes': len(content)}


def measure_profile(args, engine, image, model, delivery, items, reference, baseline):
    suffix = engine + '-' + MODELS[model]['label'] + '-' + delivery
    wait_for_gpu_settle(args.gpu_index, baseline['used_mib'] + 128, 90, args.allow_shared_gpu)
    # GPU baseline is sampled before CUDA/model loading, not after warmup.
    before = gpu_snapshot(args.gpu_index)
    with worker(args, engine, image, suffix) as (container, ready, info):
        if info['models'][model]['revision'] != MODELS[model]['revision']:
            raise ValueError('Candidate checkpoint revision differs from the benchmark catalog.')
        with GpuSampler(args.gpu_index, args.sample_interval) as sampler:
            started = time.perf_counter()
            request_json('POST', args.base_url + '/studio/models/load', {'model': model}, timeout=900)
            load_seconds = time.perf_counter() - started
        cold_gpu = sampler.summary(before['used_mib'])
        voice = register_reference(args.base_url, *reference) if MODELS[model]['mode'] == 'clone' else None
        def call(item, seed):
            options = payload(item, seed=seed, max_tokens=args.max_new_tokens, chunk_size=args.chunk_size)
            if voice:
                options['voice_profile'] = voice
            return generate(args.base_url, options, streaming=delivery == 'streaming', request_id=str(uuid.uuid4()))
        warmups = []
        for index in range(args.warmup_calls):
            _, metrics = call(items[index % len(items)], 9001 + index)
            warmups.append(metrics)
        calls = []
        folder = args.artifacts / args.run_id / suffix
        folder.mkdir(parents=True, exist_ok=True)
        for index, item in enumerate(items, 1):
            record = {**item, 'seed': stable_seed(item['call_id'])}
            try:
                with GpuSampler(args.gpu_index, args.sample_interval) as sampler:
                    audio, metrics = call(item, record['seed'])
                record.update(metrics); record['gpu'] = sampler.summary(before['used_mib'])
                artifact = folder / (re.sub(r'[^a-zA-Z0-9_.-]', '_', item['call_id'].split('/')[-1]) + '.wav')
                artifact.write_bytes(audio)
                record['artifact'] = artifact.relative_to(args.artifacts).as_posix()
            except Exception as error:
                record.update(error_stage='tts', error=safe_error(error))
            calls.append(record)
            with (folder / 'calls.jsonl').open('a', encoding='utf-8') as file:
                file.write(json.dumps(record, ensure_ascii=False) + '\n')
            print(f"[{suffix} {index}/{len(items)}] {item['call_id']}: {record.get('rtf', 'ERROR')}", flush=True)
        return {'engine': engine, 'model': model, 'revision': MODELS[model]['revision'], 'delivery': delivery,
            'incremental_waveforms': info['incremental_waveforms'], 'image': image_metadata(image),
            'worker_harness': info.get('harness'),
            'runtime_versions': version_metadata(container), 'api_ready_seconds': ready,
            'cold_load_seconds': round(load_seconds, 6), 'cold_load_gpu': cold_gpu,
            'warmups': warmups, 'gpu_baseline': before, 'container_memory': container_memory(container),
            'status_after': request_json('GET', args.base_url + '/tts/status'), 'calls': calls}


def run(args):
    items = selected_workload(args)
    if args.plan:
        print(json.dumps(plan(args, items), ensure_ascii=False, indent=2))
        return 0
    if not args.asr_url.startswith(('http://', 'https://')):
        raise ValueError('Set --asr-url or QWEN_STUDIO_ASR_URL to the existing remote ASR service.')
    asr = asr_inventory(args.asr_url)
    items = selected_workload(args, asr['supported_languages'])
    configuration = plan(args, items)
    images = {'native': args.native_image, 'faster': args.faster_image}
    needs_reference = any(item['mode'] == 'clone' for item in items)
    for engine in set(args.backends) | ({'faster'} if needs_reference and not args.reference_audio else set()):
        image_metadata(images[engine])
    profiles = []
    started = now_iso()
    with isolated_gpu(args):
        hardware = gpu_snapshot(args.gpu_index)
        if hardware is None:
            raise RuntimeError('NVIDIA telemetry is required for controlled benchmarks.')
        hardware = wait_for_gpu_settle(args.gpu_index, hardware['used_mib'] + 128, 90, args.allow_shared_gpu)
        if needs_reference:
            print('Preparing the shared reference outside all measured calls.', flush=True)
            audio, reference = prepare_reference(args, args.faster_image)
        else:
            audio, reference = b'', {'sha256': None, 'text': '', 'source': 'not used'}
        for spec in configuration['profiles']:
            model_items = [item for item in items if item['model'] == spec['model']]
            profiles.append(measure_profile(args, spec['engine'], images[spec['engine']], spec['model'],
                spec['delivery'], model_items, (audio, reference['text']), hardware))
        wait_for_gpu_settle(args.gpu_index, hardware['used_mib'] + 128, 90, args.allow_shared_gpu)
    # No ASR call overlaps any TTS measurement window. Its service stays remote.
    first = next((call for profile in profiles for call in profile['calls'] if call.get('artifact')), None)
    if first:
        try:
            transcribe(args.asr_url, (args.artifacts / first['artifact']).read_bytes(), first['asr_language'], 'warmup')
        except Exception as error:
            asr['warmup_error'] = safe_error(error)
    for profile in profiles:
        for item in profile['calls']:
            if item.get('error'):
                continue
            try:
                item.update(judge(args.asr_url, (args.artifacts / item['artifact']).read_bytes(), item))
            except Exception as error:
                item.update(error_stage='asr', error=safe_error(error))
        profile['summary'] = backend_summary(profile['calls'])
        ttfa = [call['client_ttfa_ms'] for call in profile['calls'] if call.get('client_ttfa_ms') is not None]
        profile['ttfa_median_ms'] = statistics.median(ttfa) if ttfa else None
    run = {'schema': 1, 'run_id': args.run_id, 'suite': args.suite, 'started_at': started, 'finished_at': now_iso(),
        'comment': args.comment, 'preliminary': args.no_write, 'hardware': hardware, 'config': configuration,
        'workload_sha256': configuration['workload_sha256'], 'reference': reference, 'asr': asr,
        'host_harness': harness_metadata(), 'profiles': profiles, 'comparisons': compare_profiles(profiles)}
    output = args.artifacts / args.run_id / 'run.json'; output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(run, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not args.no_write:
        with exclusive(args.results.with_suffix('.json.lock')):
            data = append_run(args.results, run)
            if args.suite == 'baseline':
                render_baseline(data, args.reports)
            elif args.suite == 'backends':
                render_pilot(data, args.reports)
            else:
                render_streaming(data, args.reports)
    errors = sum(profile['summary']['overall']['errors'] for profile in profiles)
    print(f"Finished {len(profiles)} profiles, {errors} transport/inference/judge errors. Local evidence: {output}", flush=True)
    return 1 if errors else 0


def main(argv=None):
    args = parse_args(argv)
    if args.suite == 'full':
        from benchmarks.full import run_full
        return run_full(args)
    if args.suite in {'ssml', 'queue'}:
        from benchmarks.supplemental import run_supplemental
        return run_supplemental(args)
    return run(args)


if __name__ == '__main__':
    raise SystemExit(main())
