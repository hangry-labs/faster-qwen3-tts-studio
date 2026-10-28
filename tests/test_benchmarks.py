"""Offline benchmark qualification: local synthetic HTTP, no model or GPU."""
from contextlib import contextmanager
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import base64
import hashlib
import io
import json
import struct
import subprocess
import threading
import urllib.error
import urllib.request
from unittest.mock import patch
import wave
from defusedxml import ElementTree as ET
from defusedxml.common import DefusedXmlException

import pytest

from benchmarks import common, lifecycle, reports, run_baseline as baseline, supplemental, full as resident
from benchmarks.catalog import MODELS, model_ids, payload, workload


def wav_bytes(seed=42):
    output = io.BytesIO()
    with wave.open(output, 'wb') as stream:
        stream.setnchannels(1); stream.setsampwidth(2); stream.setframerate(24000)
        stream.writeframes(struct.pack('<h', seed % 1000 + 1) * 2400)
    return output.getvalue()


@pytest.fixture
def service():
    state = {'requests': [], 'audio': {}, 'stream': 'complete', 'seed_offset': 0, 'fail_call': None, 'calls': 0, 'resident': []}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, payload, media='application/json'):
            if not isinstance(payload, bytes):
                payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            self.send_response(200); self.send_header('Content-Type', media)
            self.send_header('Content-Length', str(len(payload))); self.end_headers(); self.wfile.write(payload)

        def do_GET(self):
            state['requests'].append(self.path)
            if self.path == '/health/ready': self.send({'ready': True})
            elif self.path == '/v1/audio/supported_languages': self.send({'languages': ['English', 'Japanese']})
            elif self.path == '/v1/models': self.send({'data': [{'id': 'synthetic-test-judge'}]})
            elif self.path == '/tts/status': self.send({'state': 'idle', 'queue_depth': 0, 'resident_models': state['resident']})
            elif self.path == '/benchmark/memory': self.send({'allocated_mib': 20, 'reserved_mib': 30,
                'peak_allocated_mib': 25, 'peak_reserved_mib': 35})
            else: self.send({})

        def do_PUT(self):
            state['requests'].append(self.path)
            options = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            state['resident'] = [x['model'] for x in options['model_policy']['workflows'].values() if x['keep_loaded']]
            self.send(options)

        def do_POST(self):
            state['requests'].append(self.path)
            body = self.rfile.read(int(self.headers['Content-Length']))
            fields = {}
            if self.headers['Content-Type'].startswith('multipart/'):
                message = BytesParser(policy=policy.default).parsebytes(
                    ('Content-Type: ' + self.headers['Content-Type'] + '\r\nMIME-Version: 1.0\r\n\r\n').encode() + body)
                fields = {part.get_param('name', header='content-disposition'): part.get_payload(decode=True) for part in message.iter_parts()}
            if self.path == '/tts/voice-profiles':
                self.send({'id': 'test-reference'}); return
            if self.path == '/v1/audio/transcriptions':
                audio = fields['file']
                self.send({'text': state['audio'][hashlib.sha256(audio).hexdigest()], 'language': fields['language'].decode()}); return
            if self.path == '/studio/models/load':
                self.send({'loaded': True}); return
            if self.path == '/studio/models/unload':
                state['resident'] = []; self.send({'resident_models': []}); return
            if self.path == '/benchmark/memory/reset':
                self.send({}); return
            options = json.loads(fields['payload'] if fields else body)
            state['calls'] += 1
            if state['fail_call'] == state['calls']:
                self.send_error(503, 'Synthetic failure'); return
            try:
                seed = int(options['seed'])
            except (TypeError, ValueError):
                self.send_error(400, 'Invalid seed'); return
            audio = wav_bytes(seed)
            text = options['text']
            if options.get('input_type', 'text') != 'text':
                try:
                    text = ' '.join(' '.join(ET.fromstring(text).itertext()).split())
                except (ET.ParseError, DefusedXmlException):
                    self.send_error(400, 'Invalid SSML'); return
            state['audio'][hashlib.sha256(audio).hexdigest()] = text
            metrics = {'seed': seed + int(state['seed_offset']), 'duration_s': .1, 'generation_ms': 1, 'model_load_ms': 0}
            if self.path == '/tts/events':
                events = [{'type': 'chunk', 'audio_b64': base64.b64encode(audio).decode()}]
                if state['stream'] == 'error': events.append({'type': 'error', 'message': 'Synthetic stream failure'})
                elif state['stream'] == 'complete': events.append({'type': 'done', 'metrics': metrics})
                self.send(b''.join(('data: ' + json.dumps(event) + '\n\n').encode() for event in events), 'text/event-stream')
            else:
                self.send_response(200); self.send_header('Content-Type', 'audio/wav')
                self.send_header('X-Qwen-Metrics', json.dumps(metrics)); self.send_header('Content-Length', str(len(audio)))
                self.end_headers(); self.wfile.write(audio)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', state
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


@pytest.mark.parametrize('changes', [
    {'seed': '42\r\nInjected: header'},
    {'input_type': 'ssml', 'text': '<!DOCTYPE speak [<!ENTITY test "expanded">]><speak>&test;</speak>'},
])
def test_synthetic_service_rejects_invalid_seed_and_xml_entities(service, changes):
    url, _ = service
    data = json.dumps({'seed': 42, 'text': 'Safe text', **changes}).encode()
    request = urllib.request.Request(url + '/tts/generate', data=data,
                                     headers={'Content-Type': 'application/json'})
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(request, timeout=5)
    assert error.value.code == 400
    assert error.value.headers.get('Injected') is None


def test_full_catalog_has_360_calls_per_engine_and_checkpoint_separation():
    cases = workload(model_ids('all'))
    assert len(cases) == 360
    assert len({case['language'] for case in cases}) == 10
    assert len({case['call_id'] for case in cases}) == 360
    assert len([case for case in cases if case['mode'] == 'clone']) == 60
    assert len([case for case in cases if case['mode'] == 'design']) == 100
    assert all(MODELS[case['model']]['mode'] == case['mode'] for case in cases)
    assert len(workload(model_ids('all'), supported=['English'])) == 36
    with pytest.raises(ValueError, match='Unknown language'):
        workload(model_ids('all'), languages='Norwegian')


def test_default_baseline_uses_only_resident_06_profiles_and_shared_smoke_cannot_publish():
    args = baseline.parse_args([])
    assert len(baseline.selected_workload(args)) == 130
    assert all('0.6B' in model for model in args.models)
    with pytest.raises(SystemExit):
        baseline.parse_args(['--allow-shared-gpu'])
    args = baseline.parse_args(['--allow-shared-gpu', '--no-write'])
    assert baseline.plan(args, baseline.selected_workload(args))['shared_gpu'] is True


def test_docker_output_is_decoded_as_utf8_on_windows(monkeypatch):
    captured = {}
    def run(args, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(args, 0, stdout='Unicode output', stderr='')
    monkeypatch.setattr(common.subprocess, 'run', run)
    common.docker('logs', 'owned-worker')
    assert captured['encoding'] == 'utf-8' and captured['errors'] == 'replace'


@pytest.mark.parametrize('suite', ['baseline', 'backends', 'streaming', 'ssml', 'queue'])
def test_plan_never_performs_docker_network_or_gpu_operations(monkeypatch, suite, capsys):
    def forbidden(*args, **kwargs):
        pytest.fail('Planning attempted a real operation')
    monkeypatch.setattr(baseline, 'asr_inventory', forbidden)
    monkeypatch.setattr(baseline, 'gpu_snapshot', forbidden)
    monkeypatch.setattr(lifecycle, 'docker', forbidden)
    monkeypatch.setattr(supplemental, 'gpu_snapshot', forbidden)
    assert baseline.main(['--suite', suite, '--plan']) == 0
    assert json.loads(capsys.readouterr().out)['GPU_execution'] is False


@pytest.mark.parametrize('options', [['--models', 'nonexistent'], ['--languages', 'Norwegian', '--plan'],
    ['--warmup-calls', '0'], ['--sample-interval', '0'], ['--clients', '99'], ['--chunk-size', '65'],
    ['--backends', 'nano'], ['--reference-text', 'Unpaired'], ['--max-new-tokens', '601']])
def test_invalid_benchmark_configuration_fails_before_execution(options):
    with pytest.raises((SystemExit, ValueError)):
        baseline.main(options)


def test_vocabulary_controls_and_seed_are_qwen_specific():
    item = workload(model_ids('0.6B-CustomVoice'), languages='Japanese')[0]
    options = payload(item, seed=common.stable_seed(item['call_id']))
    assert options['voice'] == 'Ono_Anna'
    assert not {'cfg_value', 'inference_timesteps', 'denoise', 'device'} & set(options)
    assert options['seed'] == common.stable_seed(item['call_id'])
    assert common.stable_seed(item['call_id']) != common.stable_seed(item['call_id'] + 'x')


def test_transport_distinguishes_complete_from_first_streamed_audio(service):
    url, state = service
    options = {'text': '测试音频。', 'seed': 42}
    audio, complete = common.generate(url, options)
    streamed, metrics = common.generate(url, options, streaming=True)
    assert streamed == audio
    assert complete['client_ttfa_ms'] is None
    assert 0 < metrics['client_ttfa_ms'] <= metrics['tts_seconds'] * 1000
    assert complete['response_seed'] == metrics['response_seed'] == 42
    assert common.wav_duration(audio) == (.1, 24000)
    state['seed_offset'] = 1
    with pytest.raises(ValueError, match='fixed seed'):
        common.generate(url, options)


@pytest.mark.parametrize('kind', ['truncated', 'error'])
def test_truncated_and_error_streams_are_not_successes(service, kind):
    url, state = service; state['stream'] = kind
    with pytest.raises(RuntimeError):
        common.generate(url, {'text': 'A test.', 'seed': 42}, streaming=True)


def test_vox_normalization_percentiles_and_error_accounting():
    assert common.normalize_transcript('ＡＢＣ, Straße! 中文。') == 'abcstrasse中文'
    assert common.similarity('Hello, WORLD!', 'hello world') == 100
    assert common.percentile([1, 2, 3, 4, 5], .95) == 4.8
    calls = [{'case_id': 'test', 'transcript_normalized': 'hello'}, {'case_id': 'test', 'error': 'failed'}]
    assert common.consistency(calls) == (0, 1)
    summary = common.summarize_calls([{'error': 'failed'}])
    assert summary['completed'] == 0 and summary['errors'] == 1 and summary['rtf_median'] is None


def test_ssml_requires_all_ten_ordered_endings_and_the_final_tail():
    exact = supplemental.evaluate_transcript(supplemental.EXPECTED_TEXT)
    assert exact['passed'] and exact['turn_endings_detected'] == exact['ordered_turn_endings'] == 10
    assert not supplemental.evaluate_transcript(' '.join(supplemental.DIALOGUE_TURNS[:-1]))['passed']
    assert not supplemental.evaluate_transcript(' '.join(reversed(supplemental.DIALOGUE_TURNS)))['passed']
    assert not supplemental.evaluate_transcript(supplemental.EXPECTED_TEXT + ' additional unwanted ending')['passed']
    assert len(supplemental.seeds_for_rounds(7)) == 7
    for kind, document in supplemental.documents().items():
        root = ET.fromstring(document)
        assert len(list(root)) == 10
        assert {element.attrib['name'] for element in root} == {'Ryan', 'Aiden'}
        assert any('direction' in key for element in root for key in element.attrib) == (kind == 'ssml-h')


def test_exclusive_locks_do_not_remove_another_runs_lock(tmp_path):
    path = tmp_path / 'gpu.lock'
    with lifecycle.exclusive(path):
        token = path.read_text()
        with pytest.raises(RuntimeError, match='lock exists'):
            with lifecycle.exclusive(path):
                pass
        assert path.read_text() == token
    assert not path.exists()


def test_container_cleanup_is_scoped_to_the_exact_run(monkeypatch):
    actions = []
    monkeypatch.setattr(lifecycle, 'inspect_container', lambda _: {'Config': {'Labels': {
        lifecycle.OWNER_LABEL: lifecycle.OWNER, lifecycle.OWNER_LABEL + '.run': 'other-run'}}})
    monkeypatch.setattr(lifecycle, 'docker', lambda *args, **kwargs: actions.append(args))
    with pytest.raises(RuntimeError, match='another run'):
        lifecycle.remove_owned('candidate', 'our-run')
    assert not actions


def test_worker_cleanup_still_runs_if_docker_start_times_out(monkeypatch, tmp_path):
    removed = []
    monkeypatch.setattr(lifecycle, 'inspect_container', lambda _: None)
    def docker(*args, **kwargs):
        if args[0] == 'run':
            assert '127.0.0.1:8812:7860' in args
            assert 'device=0' in args
            assert 'type=volume,source=cache,target=/cache,readonly' in args
            raise subprocess.TimeoutExpired('docker run', 60)
        return subprocess.CompletedProcess(args, 0, '', '')
    monkeypatch.setattr(lifecycle, 'docker', docker)
    monkeypatch.setattr(lifecycle, 'remove_owned', lambda *args: removed.append(args))
    args = baseline.parse_args(['--cache-volume', 'cache', '--artifacts', str(tmp_path)])
    with pytest.raises(subprocess.TimeoutExpired):
        with lifecycle.worker(args, 'faster', 'candidate', 'profile'):
            pass
    assert len(removed) == 1


@pytest.fixture
def synthetic_gpu(monkeypatch):
    hardware = {'index': 0, 'name': 'SYNTHETIC TEST DEVICE', 'used_mib': 100, 'utilization_percent': 0}
    @contextmanager
    def worker(args, engine, image, suffix):
        args.active_container = 'synthetic-container'
        yield args.active_container, .01, {'models': MODELS, 'incremental_waveforms': engine == 'faster', 'inference_workers': 1}
    @contextmanager
    def isolated(*args):
        yield
    class Sampler:
        def __init__(self, *_): pass
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def summary(self, *_): return {'samples': 2, 'peak_delta_mib': 10}
    for module in [baseline, supplemental, resident]:
        monkeypatch.setattr(module, 'worker', worker)
        monkeypatch.setattr(module, 'isolated_gpu', isolated)
        monkeypatch.setattr(module, 'wait_for_gpu_settle', lambda *args: hardware)
        monkeypatch.setattr(module, 'gpu_snapshot', lambda *args: hardware)
        monkeypatch.setattr(module, 'GpuSampler', Sampler)
        monkeypatch.setattr(module, 'image_metadata', lambda _: {'id': 'sha256:synthetic-test-image'})
        monkeypatch.setattr(module, 'version_metadata', lambda _: {'inference_source_sha256': 'synthetic-test-source'})
        monkeypatch.setattr(module, 'container_memory', lambda _: {'current_mib': 100, 'peak_mib': 110})


@pytest.mark.parametrize('no_write', [False, True])
def test_full_multistage_runner_uses_synthetic_http_and_never_overlaps_asr(service, synthetic_gpu, tmp_path, no_write):
    url, state = service
    args = baseline.parse_args(['--backends', 'native,faster', '--models', '0.6B-CustomVoice', '--languages', 'English', '--repeats', '1',
        '--design-sentences', '1', '--asr-url', url, '--artifacts', str(tmp_path / 'artifacts'), '--reports', str(tmp_path / 'reports')]
        + (['--no-write'] if no_write else []))
    args.base_url = url
    assert baseline.run(args) == 0
    assert args.results.exists() != no_write
    assert (args.reports / 'speed/BENCHMARKS.md').exists() != no_write
    raw = json.loads((args.artifacts / args.run_id / 'run.json').read_text(encoding='utf-8'))
    assert len(raw['profiles']) == 2
    assert len(raw['profiles'][0]['warmups']) == 1
    assert raw['profiles'][0]['summary']['overall']['completed'] == 1
    assert raw['comparisons'][0]['matching_wav_hashes'] == 1
    assert raw['reference']['source'] == 'not used'
    paths = state['requests']
    assert max(index for index, path in enumerate(paths) if path == '/tts/generate') < paths.index('/v1/audio/transcriptions')
    assert url not in json.dumps(raw)


def test_fifo_batch_reuses_seeds_and_keeps_results_owned_by_call(service):
    url, _ = service
    model = model_ids('0.6B-CustomVoice')[0]
    ids = ['client-1', 'client-2', 'client-3']
    first = supplemental.run_batch(url, model, ids, 'sequential')
    second = supplemental.run_batch(url, model, ids, 'queued')
    assert first['audio'] == second['audio']
    assert {item['call_id']: item['seed'] for item in first['calls']} == {item['call_id']: item['seed'] for item in second['calls']}


def test_reports_do_not_label_failed_pairs_as_speedups():
    def profile(engine, error=False):
        return {'engine': engine, 'model': 'model', 'delivery': 'complete', 'calls': [
            {'call_id': 'same', 'seed': 42, 'sha256': 'match', **({'error': 'failed'} if error else {'tts_seconds': 1})}],
            'summary': {'overall': {'rtf_median': .5}}}
    comparison = reports.compare_profiles([profile('native'), profile('faster', True)])[0]
    assert comparison['median_rtf_speedup'] is None
    other = profile('faster'); other['calls'][0]['seed'] = 41
    with pytest.raises(ValueError, match='unmatched'):
        reports.compare_profiles([profile('native'), other])


def test_all_checkpoint_clone_paths_share_one_registered_reference(service, synthetic_gpu, tmp_path):
    url, state = service
    reference = tmp_path / 'reference.wav'; reference.write_bytes(wav_bytes(3))
    args = baseline.parse_args(['--backends', 'native,faster', '--models', '0.6B-Base,1.7B-Base', '--languages', 'English',
        '--clone-repeats', '1', '--reference-audio', str(reference), '--reference-text', 'A fixed reference.',
        '--asr-url', url, '--artifacts', str(tmp_path / 'artifacts'), '--reports', str(tmp_path / 'reports')])
    args.base_url = url
    assert baseline.run(args) == 0
    data = json.loads(args.results.read_text(encoding='utf-8'))['latest']
    assert len(data['profiles']) == 4
    assert state['requests'].count('/tts/voice-profiles') == 4
    assert data['reference']['sha256'] == hashlib.sha256(reference.read_bytes()).hexdigest()
    assert data['host_harness']['sha256']


def test_ssml_full_runner_preserves_every_turn_and_publishes_separate_reports(service, synthetic_gpu, tmp_path):
    url, _ = service
    args = baseline.parse_args(['--backends', 'native,faster', '--suite', 'ssml', '--rounds', '1', '--asr-url', url,
        '--artifacts', str(tmp_path / 'artifacts'), '--reports', str(tmp_path / 'reports')])
    args.base_url = url
    assert supplemental.run_supplemental(args) == 0
    data = json.loads(args.results.read_text(encoding='utf-8'))['latest']
    assert len(data['profiles']) == 2
    assert all(profile['passed'] and len(profile['calls']) == 2 for profile in data['profiles'])
    assert (args.reports / 'ssml/BENCHMARKS.md').exists()
    assert not (args.reports / 'speed/BENCHMARKS.md').exists()


def test_supplemental_queue_keeps_submissions_paired_and_alternates_order(service, synthetic_gpu, tmp_path, monkeypatch):
    url, _ = service
    args = baseline.parse_args(['--suite', 'queue', '--backends', 'faster', '--rounds', '2', '--clients', '2',
        '--artifacts', str(tmp_path / 'artifacts'), '--reports', str(tmp_path / 'reports')])
    args.base_url = url
    order = []
    actual_batch = supplemental.run_batch
    def batch(*args, **kwargs):
        result = actual_batch(*args, **kwargs)
        order.append(args[3])
        # Synthetic generation is faster than a monitor poll; supply the queue
        # observation independently, without replacing transport or pairing.
        result['queue']['peak_queued'] = 1 if args[3] == 'queued' else 0
        return result
    monkeypatch.setattr(supplemental, 'run_batch', batch)
    assert supplemental.run_supplemental(args) == 0
    assert order == ['sequential', 'queued', 'queued', 'sequential']
    latest = json.loads(args.results.read_text(encoding='utf-8'))['latest']
    assert latest['profiles'][0]['comparison']['matching_outputs'] == 4
    assert not (args.reports / 'speed/BENCHMARKS.md').exists()


def test_streaming_suite_does_not_overwrite_the_complete_baseline_reports(service, synthetic_gpu, tmp_path):
    url, _ = service
    report = tmp_path / 'reports/speed/BENCHMARKS.md'; report.parent.mkdir(parents=True)
    report.write_text('Existing complete baseline.', encoding='utf-8')
    args = baseline.parse_args(['--suite', 'streaming', '--models', '0.6B-CustomVoice', '--languages', 'English',
        '--repeats', '1', '--design-sentences', '1', '--asr-url', url,
        '--artifacts', str(tmp_path / 'artifacts'), '--reports', str(tmp_path / 'reports')])
    args.base_url = url
    assert baseline.run(args) == 0
    assert report.read_text() == 'Existing complete baseline.'
    assert (args.reports / 'streaming/BENCHMARKS.md').exists()


def test_cached_asset_inventory_is_model_free_and_rejects_missing_weights(tmp_path):
    from benchmarks.preflight import inventory
    snapshot = tmp_path / 'model/snapshots/revision'; snapshot.mkdir(parents=True)
    (snapshot / 'speech_tokenizer').mkdir()
    for name in ['README.md', 'config.json', 'speech_tokenizer/config.json',
        'model.safetensors', 'speech_tokenizer/model.safetensors']:
        (snapshot / name).write_bytes(b'synthetic test asset')
    files = inventory(snapshot, hash_files=True)
    assert len(files) == 5 and all(len(item['sha256']) == 64 for item in files)
    assert str(tmp_path) not in json.dumps(files)
    (snapshot / 'model.safetensors').unlink()
    with pytest.raises(ValueError, match='missing model'):
        inventory(snapshot)


def test_full_plan_is_faster_only_with_one_measured_checkpoint_at_a_time(capsys):
    args = baseline.parse_args(['--suite', 'full', '--plan'])
    assert resident.run_full(args) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan['engines'] == ['faster'] and plan['measured_calls'] == 310
    assert len(plan['resident_models_per_profile']) == 2 and len(plan['measured_models']) == 2
    assert plan['suites'] == {'baseline': 130, 'streaming': 130, 'ssml': 10, 'queue': 40}
    assert not plan['GPU_execution']
    with pytest.raises(SystemExit):
        baseline.parse_args(['--suite', 'full', '--backends', 'native,faster'])
    filtered = baseline.parse_args(['--suite', 'full', '--modes', 'clone', '--plan'])
    assert filtered.models == model_ids('0.6B-Base')
    assert resident.full_plan(filtered, baseline.selected_workload(filtered))['measured_calls'] == 60
    with pytest.raises(SystemExit):
        baseline.parse_args(['--suite', 'full', '--modes', 'design'])


@pytest.mark.parametrize('no_write', [False, True])
def test_full_baseline_keeps_one_model_through_its_suites_then_unloads_before_judging(service, synthetic_gpu, tmp_path, monkeypatch, no_write):
    url, state = service
    reference = tmp_path / 'reference.wav'; reference.write_bytes(wav_bytes(3))
    args = baseline.parse_args(['--suite', 'full', '--reference-audio', str(reference), '--reference-text', 'A fixed reference.', '--languages', 'English', '--design-sentences', '1',
        '--repeats', '1', '--clone-repeats', '1', '--rounds', '1', '--clients', '2', '--asr-url', url,
        '--artifacts', str(tmp_path / 'artifacts'), '--reports', str(tmp_path / 'reports')]
        + (['--no-write'] if no_write else []))
    args.base_url = url
    actual = supplemental.run_batch
    def batch(*args, **kwargs):
        result = actual(*args, **kwargs)
        result['queue']['peak_queued'] = int(args[3] == 'queued')
        return result
    monkeypatch.setattr(supplemental, 'run_batch', batch)
    assert resident.run_full(args) == 0
    run = json.loads((args.artifacts / args.run_id / 'run.json').read_text(encoding='utf-8'))
    assert run['config']['measured_calls'] == 10
    assert set(run['profiles']) == set(resident.SUITES)
    assert all(status['resident_models'] == [model] for model, status in run['resident_status_after_tests'].items())
    assert all(x['status']['resident_models'] == [] for x in run['teardown'].values())
    assert not run['profiles']['ssml'][0]['delivery_directions']
    assert 'h:direction' not in run['profiles']['ssml'][0]['documents']['ssml-h']
    assert run['profiles']['streaming'][0]['calls'][0]['stream_chunk_count'] == 1
    assert url not in json.dumps(run)
    paths = state['requests']
    assert paths.count('/system/settings') == 4
    assert paths.count('/studio/models/unload') == 2
    assert '/studio/models/load' not in paths
    last_tts = max(i for i, path in enumerate(paths) if path in ['/tts/generate', '/tts/events'])
    assert last_tts < paths.index('/v1/audio/transcriptions')
    assert paths.index('/studio/models/unload') < last_tts
    assert all((args.artifacts / (suite + '-results/runs.json')).exists() != no_write for suite in resident.SUITES)
    assert args.results.exists() != no_write
    if not no_write:
        assert 'Resident cohort' in (args.reports / 'memory/gpu/BENCHMARKS.md').read_text()


def test_resident_checks_reject_eviction_and_measured_loading(service):
    url, _ = service
    args = baseline.parse_args(['--suite', 'full']); args.base_url = url; args.resident_models = args.models
    with pytest.raises(RuntimeError, match='cohort changed'):
        resident.assert_resident(args)
    for metrics in [{}, {'server_metrics': {'model_load_ms': 2}}]:
        with pytest.raises(RuntimeError, match='loaded weights'):
            resident.assert_warm(metrics)
