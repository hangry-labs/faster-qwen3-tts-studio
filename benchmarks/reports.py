"""Vox-style reviewed summaries and details, with separate Qwen checkpoints."""
from pathlib import Path
from .common import backend_summary, fingerprint


def cell(value):
    return str(value).replace('|', '/').replace('\n', ' ').replace('\r', ' ').replace('<', '&lt;').replace('>', '&gt;')


def metric(value, places=3):
    return 'n/a' if value is None else f'{value:.{places}f}'


def table(headers, rows):
    return ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|'] + [
        '| ' + ' | '.join(cell(value) for value in row) + ' |' for row in rows]


def write(path, lines):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def render_baseline(data, root):
    """Rebuild all history rows, but use only the latest run for detail tables."""
    root = Path(root)
    speed, memory, quality = [], [], []
    for run in data['runs']:
        for profile in run['profiles']:
            row = profile['summary']['overall']; ram = profile['container_memory']
            identity = [run['run_id'], profile['engine'], profile['model'].split('12Hz-')[-1], profile['delivery']]
            speed.append(identity + [f"{row['completed']}/{row['calls']}", metric(row['realtime_speed'], 2),
                metric(row['rtf_median']), metric(row['rtf_p95']),
                metric(profile['ttfa_median_ms'], 1), row['tts_errors']])
            cohort = ', '.join(x.split('12Hz-')[-1] for x in profile.get('resident_models', [profile['model']]))
            torch = profile.get('torch_memory', {})
            memory.append(identity + [cohort, profile['gpu_baseline']['used_mib'], row['gpu_peak_delta_mib'],
                profile['cold_load_gpu'].get('peak_delta_mib'), torch.get('peak_allocated_mib', 'n/a'),
                torch.get('peak_reserved_mib', 'n/a'), ram['current_mib'], ram['peak_mib']])
            quality.append(identity + [row['quality_completed'], metric(row['exact_percent'], 2),
                metric(row['mean_similarity_percent'], 2), metric(row['min_similarity_percent'], 2),
                metric(profile['summary']['consistent_case_percent'], 2), row['errors'], run['asr']['model']])
    common = ['Run', 'Engine', 'Checkpoint', 'Delivery']
    for directory, title, note, headers, rows in [
        ('speed', 'Inference speed', 'Realtime speed is total generated audio duration / total request time; higher is better. 3.3x means 3.3 seconds of audio generated per second. RTF is request time / audio duration; lower is better. TTFA is measured only for audio events.',
            ['Completed', 'Realtime speed (×)', 'Median RTF', 'p95 RTF', 'Median client TTFA ms', 'TTS errors'], speed),
        ('memory/gpu', 'GPU memory', 'Whole-device MiB minus the pre-load baseline. Resident-cohort rows include every listed checkpoint, not just the measured model. Torch peaks and cgroup RAM cover that worker and its entire cohort; loading is separate from warmed calls.',
            ['Resident cohort', 'VRAM baseline MiB', 'Warm peak delta MiB', 'Load peak delta MiB', 'Torch peak allocated MiB', 'Torch peak reserved MiB', 'RAM current MiB', 'RAM peak MiB'], memory),
        ('speech-quality', 'Speech quality', 'ASR transcript fidelity is a comparative signal, not naturalness, expressiveness or speaker identity. Listening review remains necessary.',
            ['Judged', 'Exact %', 'Mean similarity %', 'Minimum %', 'Repeat consistency %', 'Errors', 'ASR model'], quality),
    ]:
        write(root / directory / 'BENCHMARKS.md', ['# ' + title, '', note, '',
            *table(common + headers, rows), '', 'See [DETAILS.md](DETAILS.md) for the latest run and methodology.', ''])
    run = data['latest']
    details = {key: ['# ' + title + ' details', '', f"Run `{run['run_id']}` on {cell(run['hardware']['name'])}.",
        f"Workload SHA-256: `{run['workload_sha256']}`. Reference SHA-256: `{run['reference']['sha256']}`.",
        'Fixed per-call seeds, concurrency one, explicit settings and discarded warmups. Checkpoints are never pooled.', '']
        for key, title in [('speed', 'Inference speed'), ('memory/gpu', 'GPU memory'), ('speech-quality', 'Speech quality')]}
    for profile in run['profiles']:
        name = f"{profile['engine']} / {profile['model'].split('12Hz-')[-1]} / {profile['delivery']}"
        for key in details:
            details[key] += ['## ' + name, '',
                f"Image `{profile['image']['id']}`; source `{profile['runtime_versions']['inference_source_sha256']}`.",
                f"API ready {profile['api_ready_seconds']:.3f}s; cold load {profile['cold_load_seconds']:.3f}s; "
                f"discarded warmups {len(profile['warmups'])}. Incremental waveform support: {profile['incremental_waveforms']}.", '']
            if profile.get('resident_models'):
                details[key] += ['Resident cohort: ' + ', '.join('`' + x.split('12Hz-')[-1] + '`' for x in profile['resident_models']) + '.',
                    'Cold load and memory cover the listed resident set. The full product run retains each checkpoint through its applicable suites, then unloads it before the next.', '']
        groups = [('Mode: ' + key, row) for key, row in profile['summary']['by_mode'].items()] + [
            ('Language: ' + key, row) for key, row in profile['summary']['by_language'].items()]
        details['speed'] += table(['Group', 'Completed', 'Realtime speed (×)', 'Median RTF', 'p95 RTF'], [
            [name, f"{row['completed']}/{row['calls']}", metric(row['realtime_speed'], 2), metric(row['rtf_median']), metric(row['rtf_p95'])] for name, row in groups]) + ['']
        details['memory/gpu'] += table(['Group', 'Warm peak delta MiB', 'Measured calls'], [
            [name, row['gpu_peak_delta_mib'], row['calls']] for name, row in groups]) + ['']
        details['speech-quality'] += table(['Group', 'Judged', 'Exact %', 'Mean similarity %', 'Minimum %', 'Errors'], [
            [name, row['quality_completed'], row['exact_percent'], row['mean_similarity_percent'], row['min_similarity_percent'], row['errors']] for name, row in groups]) + ['']
        hardest = sorted((call for call in profile['calls'] if 'similarity_percent' in call), key=lambda item: item['similarity_percent'])[:20]
        details['speech-quality'] += ['### Hardest calls', '', *table(['Call', 'Expected', 'Transcript', 'Similarity %'], [
            [call['call_id'], call['text'], call['transcript'], call['similarity_percent']] for call in hardest]), '']
    for key, lines in details.items():
        write(root / key / 'DETAILS.md', lines)
    reviewed = [f'[{label}]({path})' for label, path in [('0.6B baseline', 'BASELINE_RESULTS.md'),
        ('1.7B baseline', 'BASELINE_1.7B_RESULTS.md')] if (root / path).exists()]
    write(root / 'BENCHMARKS.md', ['# Faster Qwen3-TTS Studio benchmarks', '',
        f"Latest recorded baseline: `{run['run_id']}` on {cell(run['hardware']['name'])}.",
        'Review the separate speed, memory and transcript-fidelity reports. Model sizes and workflows are not pooled.', '',
        *(['Reviewed summaries: ' + ', '.join(reviewed) + '.', ''] if reviewed else []),
        *table(['Area', 'Report'], [[name, f'[{name}]({path}/BENCHMARKS.md)'] for name, path in [
            ('Inference speed', 'speed'), ('GPU memory', 'memory/gpu'), ('Speech quality', 'speech-quality'),
            ('Backend comparison', 'backend_comparison'), ('Streaming', 'streaming'), ('SSML', 'ssml'), ('Queue', 'inference_queue')]]),
        '', 'Methodology and interpretation: [README.md](README.md).', ''])


def compare_profiles(profiles):
    comparisons = []
    for faster in [profile for profile in profiles if profile['engine'] == 'faster']:
        native = next((profile for profile in profiles if profile['engine'] == 'native' and
            profile['model'] == faster['model'] and profile['delivery'] == faster['delivery']), None)
        if native is None:
            continue
        left, right = native['calls'], faster['calls']
        if [(item['call_id'], item['seed']) for item in left] != [(item['call_id'], item['seed']) for item in right]:
            raise ValueError('Cannot compare unmatched workloads or seeds.')
        valid = all('tts_seconds' in item and not item.get('error') for item in left + right)
        slower_rtf, faster_rtf = native['summary']['overall']['rtf_median'], faster['summary']['overall']['rtf_median']
        comparisons.append({'model': faster['model'], 'delivery': faster['delivery'], 'complete_pairs': valid,
            'median_rtf_speedup': slower_rtf / faster_rtf if valid and faster_rtf else None,
            'matching_wav_hashes': sum(a.get('sha256') == b.get('sha256') and a.get('sha256') is not None for a, b in zip(left, right)),
            'pairs': len(left), 'note': 'Different generation loops are not required to be byte-identical.'})
    return comparisons


def render_pilot(data, root):
    rows, timings = [], []
    for run in data['runs']:
        for profile in run['profiles']:
            row = profile['summary']['overall']
            timings.append([run['run_id'], profile['engine'], profile['model'].split('12Hz-')[-1],
                row['completed'], metric(row['rtf_median']), metric(row['rtf_p95']), row['errors']])
        for comparison in run.get('comparisons', []):
            rows.append([run['run_id'], comparison['model'].split('12Hz-')[-1], comparison['delivery'],
                metric(comparison['median_rtf_speedup'], 2), comparison['matching_wav_hashes'], comparison['pairs']])
    write(Path(root) / 'backend_comparison/BENCHMARKS.md', ['# Backend comparison', '',
        'Same pinned checkpoint, corpus, reference and explicit settings. Only complete matched workloads receive a speedup value.', '',
        *table(['Run', 'Engine', 'Checkpoint', 'Completed', 'Median RTF', 'p95 RTF', 'Errors'], timings), '',
        *table(['Run', 'Checkpoint', 'Delivery', 'Median RTF speedup', 'Identical WAVs', 'Pairs'], rows), ''])
    lines = ['# Backend comparison details', '', 'The four-scenario pilot is diagnostic; use the full multilingual baseline for release decisions.', '']
    for profile in data['latest']['profiles']:
        lines += ['## ' + profile['engine'] + ' / ' + profile['model'].split('12Hz-')[-1], '',
            *table(['Call', 'Wall s', 'Audio s', 'RTF', 'WAV SHA-256', 'Error stage'], [
                [call['call_id'], call.get('tts_seconds', 'n/a'), call.get('audio_seconds', 'n/a'), call.get('rtf', 'n/a'),
                    call.get('sha256', 'n/a'), call.get('error_stage', '')] for call in profile['calls']]), '']
    write(Path(root) / 'backend_comparison/DETAILS.md', lines)


def render_streaming(data, root):
    rows = []
    for run in data['runs']:
        for profile in run['profiles']:
            row = profile['summary']['overall']
            rows.append([run['run_id'], profile['engine'], profile['model'].split('12Hz-')[-1],
                profile['incremental_waveforms'], row['completed'], metric(row['realtime_speed'], 2), metric(profile['ttfa_median_ms'], 1),
                metric(profile.get('ttfa_p95_ms'), 1),
                metric(row['rtf_median']), metric(row['rtf_p95']), row['errors']])
    write(Path(root) / 'streaming/BENCHMARKS.md', ['# Streaming latency', '',
        'Client TTFA starts before the HTTP request and ends at the first decoded nonempty SSE audio chunk. '
        'Standard Qwen emits one buffered recording; this is not incremental synthesis. SSE transport excludes browser playback buffering.', '',
        *table(['Run', 'Engine', 'Checkpoint', 'Incremental', 'Calls', 'Realtime speed (×)', 'Median TTFA ms', 'p95 TTFA ms', 'Median RTF', 'p95 RTF', 'Errors'], rows), ''])
    lines = ['# Streaming details', '', 'Warm client TTFA and complete request wall time are different measurements.', '']
    for profile in data['latest']['profiles']:
        lines += ['## ' + profile['engine'] + ' / ' + profile['model'].split('12Hz-')[-1], '',
            *table(['Call', 'Client TTFA ms', 'Wall s', 'Audio s', 'RTF', 'Chunks', 'Largest chunk gap ms', 'Transcript similarity %'], [
                [call['call_id'], call.get('client_ttfa_ms'), call.get('tts_seconds'), call.get('audio_seconds'),
                    call.get('rtf'), call.get('stream_chunk_count'), call.get('max_chunk_gap_ms'),
                    call.get('similarity_percent', 'n/a')] for call in profile['calls']]), '']
    write(Path(root) / 'streaming/DETAILS.md', lines)
