"""Compare streaming decoder windows with resident models and isolated allocators.

Run inside the product's NVIDIA Docker image, with this benchmark directory
mounted and a populated, read-only Hugging Face cache. Never starts ASR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

CASES = [
    ('short-en', 'English', 'The little robot opened the window and listened to the morning rain.'),
    ('long-en', 'English', 'The little robot opened the window and listened to the morning rain. '
     'Across the garden, a sleepy cat watched the birds gather beneath the old apple tree. '
     'There was no need to hurry today. The train would arrive after lunch, leaving plenty of time '
     'to make some tea and finish the story.'),
    ('long-ja', 'Japanese', '朝の雨が静かに窓をたたいていました。小さなロボットは庭を眺めながら、今日の予定を考えました。'
     '午後には友達が来るので、お茶を用意して、新しい物語を一緒に読むつもりです。急ぐ必要はありません。'
     '鳥の声を聞きながら、ゆっくりと部屋の片付けを始めました。'),
]
REFERENCE_TEXT = CASES[0][2]
DIRECTION = 'A warm adult narrator with clear, steady diction and a natural conversational voice.'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def worker(args):
    import numpy as np
    import soundfile as sf
    import torch
    import transformers
    from faster_qwen3_tts import streaming
    from faster_qwen3_tts.standalone_ui.runtime import MODELS, StudioEngine

    engine = StudioEngine()
    started = time.perf_counter()
    engine._load(args.worker)
    load_s = time.perf_counter() - started
    model = engine.model
    mode = MODELS[args.worker]['mode']
    reference = args.output / 'reference.wav'
    if args.reference_worker:
        torch.manual_seed(42)
        wave, rate = model.generate_custom_voice(text=REFERENCE_TEXT, language='English', speaker='Ryan', max_new_tokens=360)
        sf.write(reference, np.asarray(wave, dtype=np.float32).reshape(-1), rate, subtype='FLOAT')
        write_json(args.output / 'reference.json', {'text': REFERENCE_TEXT, 'seed': 42,
            'model': args.worker, 'sha256': hashlib.sha256(reference.read_bytes()).hexdigest()})
        return

    original = streaming.fast_generate_streaming
    frames = 0
    checksum = hashlib.sha256()
    def record_codes(**kwargs):
        nonlocal frames
        for codes, timing in original(**kwargs):
            frames += len(codes)
            checksum.update(codes.detach().cpu().numpy().tobytes())
            yield codes, timing
    streaming.fast_generate_streaming = record_codes
    rows = []
    for case_index, (name, language, text) in enumerate(CASES):
        options = dict(text=text, language=language, max_new_tokens=600, chunk_size=8,
                       decoder_context_frames=args.context)
        if mode == 'custom':
            options['speaker'] = 'Ryan' if language == 'English' else 'Ono_Anna'
        elif mode == 'design':
            options['instruct'] = DIRECTION
        else:
            options.update(ref_audio=str(reference), ref_text=REFERENCE_TEXT, xvec_only=False)
        method = getattr(model, {'custom': 'generate_custom_voice_streaming',
                                'design': 'generate_voice_design_streaming',
                                'clone': 'generate_voice_clone_streaming'}[mode])
        # Warm the actual prompt/clone cache and decoder shapes. Allocator state
        # is retained for every measured request in this context-only process.
        torch.manual_seed(1000 + case_index)
        for _ in method(**options):
            pass
        for repeat in range(args.repeats):
            seed = 4200 + case_index * 10 + repeat
            torch.manual_seed(seed)
            frames, checksum = 0, hashlib.sha256()
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            baseline_allocated = torch.cuda.memory_allocated() / 2**20
            baseline_reserved = torch.cuda.memory_reserved() / 2**20
            chunks, arrivals = [], []
            start = time.perf_counter()
            for wave, rate, _ in method(**options):
                if len(wave):
                    arrivals.append(time.perf_counter() - start)
                    chunks.append(np.asarray(wave, dtype=np.float32))
            torch.cuda.synchronize()
            wall = time.perf_counter() - start
            assert chunks and arrivals
            output = np.concatenate(chunks)
            assert np.isfinite(output).all()
            assert model.last_generation_stop_reason == 'eos', model.last_generation_stop_reason
            duration = len(output) / rate
            row = dict(model=args.worker, mode=mode, context=args.context, phase=args.phase,
                case=name, language=language, text=text, repeat=repeat, seed=seed, wall_s=wall,
                duration_s=duration, realtime=duration/wall, ttfa_ms=arrivals[0]*1000,
                max_chunk_gap_ms=max([b-a for a,b in zip(arrivals, arrivals[1:])] or [0])*1000,
                chunks=len(chunks), codec_frames=frames, codec_sha256=checksum.hexdigest(),
                waveform_sha256=hashlib.sha256(output.tobytes()).hexdigest(),
                baseline_allocated_mib=baseline_allocated, baseline_reserved_mib=baseline_reserved,
                peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20,
                peak_reserved_mib=torch.cuda.max_memory_reserved()/2**20,
                stop_reason=model.last_generation_stop_reason)
            if repeat == 0:
                audio_name = f'{args.worker.rsplit("-", 2)[-2]}-{mode}-{args.context}-{args.phase}-{name}.wav'
                sf.write(args.output / audio_name, output, rate, subtype='FLOAT')
                row['audio'] = audio_name
            rows.append(row)
            print(json.dumps({key: row[key] for key in ['model','context','phase','case','repeat','realtime','peak_allocated_mib']}), flush=True)
    result = dict(rows=rows, load_s=load_s, torch=torch.__version__, transformers=transformers.__version__,
                  gpu=torch.cuda.get_device_name(), model_revision=MODELS[args.worker]['revision'])
    write_json(args.output / f'{args.worker.rsplit("/",1)[-1]}-{args.phase}-{args.context}.json', result)


def report(output):
    files = sorted(output.glob('Qwen3-TTS-*.json'))
    if not files:
        raise ValueError('No completed decoder-context workers found.')
    rows = [row for path in files for row in json.loads(path.read_text(encoding='utf-8'))['rows']]
    summaries = []
    for model in dict.fromkeys(row['model'] for row in rows):
        for context in [25,100]:
            group = [row for row in rows if row['model']==model and row['context']==context]
            if not group:
                raise ValueError('Incomplete counterbalanced comparison; a context is missing.')
            summaries.append(dict(model=model, context=context, samples=len(group),
                realtime=sum(r['duration_s'] for r in group)/sum(r['wall_s'] for r in group),
                median_ttfa_ms=statistics.median(r['ttfa_ms'] for r in group),
                peak_allocated_mib=max(r['peak_allocated_mib'] for r in group),
                peak_reserved_mib=max(r['peak_reserved_mib'] for r in group)))
    pairs = {}
    for row in rows:
        key = (row['model'], row['case'], row['repeat'])
        pairs.setdefault(key, []).append(row)
    for group in pairs.values():
        if (len(group) != 4 or {r['phase'] for r in group} != {0,1,2,3}
                or any(r['context'] != [25,100,100,25][r['phase']] for r in group)):
            raise ValueError('Incomplete or duplicated counterbalanced comparison; retain raw evidence without a report.')
    identical_codes = all(len({r['codec_sha256'] for r in group})==1 for group in pairs.values())
    result = dict(samples=len(rows), paired_cases=len(pairs), identical_codec_tokens=identical_codes,
                  summaries=summaries, rows=rows)
    write_json(output/'results.json', result)
    metadata = json.loads(files[0].read_text(encoding='utf-8'))
    lines = ['# Streaming decoder context comparison', '',
        f'Hardware: {metadata["gpu"]}. Torch {metadata["torch"]}; Transformers {metadata["transformers"]}.', '',
        'Resident, warmed NVIDIA inference; one checkpoint/context per fresh process. Context order is 25, 100, 100, 25.',
        'Three prompts (short English, long English and long Japanese), two measured seeds per prompt per phase. '
        'Model loading, graph capture and prompt warmups are excluded. No audio encoding, queue or network time is included.',
        'Codec checksums collect the same small CPU copy in both contexts. Allocator memory is retained within each worker; '
        'separate context workers prevent a previous 100-frame run from inflating the 25-frame reserved-memory peak.', '',
        f'Measured requests: {len(rows)}. Identical codec tokens across contexts/repeats of the same seed: {identical_codes}.', '',
        '| Checkpoint | Context frames | Realtime speed (×) | Median first audio (ms) | Peak allocated (MiB) | Peak reserved (MiB) |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for row in summaries:
        lines.append(f'| {row["model"].removeprefix("Qwen/Qwen3-TTS-12Hz-")} | {row["context"]} | {row["realtime"]:.3f} | {row["median_ttfa_ms"]:.1f} | {row["peak_allocated_mib"]:.1f} | {row["peak_reserved_mib"]:.1f} |')
    lines += ['', 'Torch allocated peaks measure live tensors; reserved peaks include its caching allocator and captured graphs. '
              'These are not whole-device VRAM measurements. Compare individual prompts and phases in results.json; '
              'aggregate speed is workload dependent. Short output may finish before a 100-frame rolling window is exercised.', '',
              'Matching codec tokens establishes controlled reconstruction inputs, not perceptual quality. '
              'Waveforms may differ because the decoder sees different context. Transcript checks and listening remain separate.', '']
    (output/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--models', default='all')
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--worker')
    parser.add_argument('--context', type=int, choices=[25,100])
    parser.add_argument('--phase', type=int)
    parser.add_argument('--reference-worker', action='store_true')
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.report_only:
        report(args.output)
        return
    if args.worker:
        worker(args)
        return
    if not 1 <= args.repeats <= 10:
        parser.error('repeats must be from 1 to 10')
    if any(args.output.glob('Qwen3-TTS-*.json')):
        parser.error('Choose a fresh output directory to keep experiments separate.')
    from faster_qwen3_tts.standalone_ui.model_catalog import MODELS
    models = list(MODELS) if args.models=='all' else [name if name.startswith('Qwen/') else 'Qwen/Qwen3-TTS-12Hz-'+name for name in args.models.split(',')]
    if not models or any(name not in MODELS for name in models):
        parser.error('Unknown checkpoint')
    command = [sys.executable, '-m', 'benchmarks.decoder_context', '--output', str(args.output)]
    if any(MODELS[name]['mode']=='clone' for name in models):
        subprocess.run(command + ['--worker','Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice','--reference-worker'], check=True)
    for model in models:
        for phase, context in enumerate([25,100,100,25]):
            subprocess.run(command + ['--worker',model,'--phase',str(phase),'--context',str(context),'--repeats',str(args.repeats)], check=True)
    result = report(args.output)
    if not result['identical_codec_tokens']:
        raise RuntimeError('Codec token mismatch: investigate before attributing differences to context.')
    print(f'Completed {result["samples"]} measured requests.', flush=True)


if __name__ == '__main__':
    main()
