"""Host-readable benchmark catalog; importing it never imports Torch."""
from pathlib import Path
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
MODELS = runpy.run_path(str(ROOT / 'src/faster_qwen3_tts/standalone_ui/model_catalog.py'))['MODELS']
CORPUS_PATH = ROOT / 'benchmarks/corpus.json'
REFERENCE_TEXT = 'The little robot opened the window and listened to the morning rain.'
REFERENCE_INSTRUCTION = 'A calm adult narrator with clear, natural diction and a warm, steady voice.'


def model_ids(value):
    selected = []
    for name in value.split(','):
        identity = name.strip()
        if identity == 'all':
            selected.extend(MODELS)
            continue
        if not identity.startswith('Qwen/'):
            identity = 'Qwen/Qwen3-TTS-12Hz-' + identity
        if identity not in MODELS:
            raise ValueError(f'Unknown checkpoint: {name}')
        selected.append(identity)
    if not selected:
        raise ValueError('Select at least one model.')
    return list(dict.fromkeys(selected))


def workload(models, *, languages='', supported=None, design_sentences=2, repeats=5,
             clone_repeats=3, modes=('custom', 'design', 'clone'), corpus_path=CORPUS_PATH):
    corpus = json.loads(Path(corpus_path).read_text(encoding='utf-8'))
    filters = {name.strip().casefold() for name in languages.split(',') if name.strip()}
    supported = {name.casefold(): name for name in supported} if supported is not None else None
    entries = [entry for entry in corpus['languages'] if not filters or entry['language'].casefold() in filters or entry['slug'] in filters]
    matched = {entry['language'].casefold() for entry in entries} | {entry['slug'] for entry in entries}
    if filters - matched:
        raise ValueError('Unknown language filter: ' + ', '.join(sorted(filters - matched)))
    cases = []
    for model in models:
        mode = MODELS[model]['mode']
        if mode not in modes:
            continue
        for entry in entries:
            language = entry['language']
            if supported is not None and language.casefold() not in supported:
                continue
            prompts = [{'text': entry['clone_text']}] if mode == 'clone' else entry['design'][:design_sentences]
            if mode != 'clone' and len(prompts) < design_sentences:
                raise ValueError(f'Not enough corpus sentences for {language}.')
            for index, prompt in enumerate(prompts, 1):
                for repeat in range(1, (clone_repeats if mode == 'clone' else repeats) + 1):
                    case_id = f"{MODELS[model]['label']}/{entry['slug']}_{mode}_{index:02d}"
                    cases.append({'case_id': case_id, 'call_id': case_id + f'_r{repeat}', 'model': model,
                        'mode': mode, 'language': language, 'asr_language': supported[language.casefold()] if supported else language,
                        'text': prompt['text'], 'instruct': prompt.get('instruct', '') if mode == 'design' else '',
                        'repeat': repeat})
    if not cases:
        raise ValueError('No checkpoint/language/workflow cases matched the ASR intersection.')
    if len({case['call_id'] for case in cases}) != len(cases):
        raise ValueError('Corpus produces duplicate call ids.')
    return cases


def payload(item, *, seed, max_tokens=600, chunk_size=8):
    speaker = {'Chinese': 'Vivian', 'Japanese': 'Ono_Anna', 'Korean': 'Sohee'}.get(item['language'], 'Ryan')
    return {'text': item['text'], 'model': item['model'], 'mode': item['mode'], 'voice': speaker,
        'language': item['language'], 'instruct': item.get('instruct', ''), 'seed': seed,
        'input_type': 'text', 'output_format': 'wav', 'non_streaming_mode': item['mode'] != 'clone',
        'temperature': .9, 'top_k': 50, 'repetition_penalty': 1.05, 'max_new_tokens': max_tokens,
        'chunk_size': chunk_size, 'normalize_loudness': False, 'protect_long_audio': False, 'speed': 1}
