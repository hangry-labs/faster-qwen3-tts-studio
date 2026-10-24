"""Generate real GPU samples through Studio and check them with Qwen3 ASR.

Writes local evidence under artifacts/, never into distributable example assets.
"""
import argparse
import base64
import io
import json
import os
from pathlib import Path
import re
import uuid
from urllib.request import Request, urlopen
import wave

TEXT = 'The little robot opened the window and listened to the morning rain.'


def multipart(fields, files=None):
    boundary = 'qwen' + uuid.uuid4().hex
    parts = []
    for key, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
    for key, (name, content) in (files or {}).items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"; filename="{name}"\r\nContent-Type: audio/wav\r\n\r\n'.encode() + content + b'\r\n')
    return b''.join(parts) + f'--{boundary}--\r\n'.encode(), 'multipart/form-data; boundary=' + boundary


def post(url, fields, files=None):
    body, content_type = multipart(fields, files)
    return urlopen(Request(url, data=body, headers={'Content-Type': content_type}), timeout=600)


def word_error(reference, actual):
    expected = re.findall(r'\w+', reference.lower())
    actual = re.findall(r'\w+', actual.lower())
    previous = list(range(len(actual) + 1))
    for row, word in enumerate(expected, 1):
        current = [row]
        for column, other in enumerate(actual, 1):
            current.append(min(current[-1] + 1, previous[column] + 1, previous[column - 1] + (word != other)))
        previous = current
    return previous[-1] / max(1, len(expected))


def generate(base, options, reference=None, streaming=False):
    files = {'reference': ('reference.wav', reference)} if reference else None
    with post(base + '/studio/generate' + ('/stream' if streaming else ''), {'options': json.dumps(options)}, files) as response:
        if not streaming:
            result = json.load(response)
            return base64.b64decode(result['audio_b64']), result['metrics']
        chunks, metrics = [], None
        for line in response:
            if not line.startswith(b'data: '):
                continue
            event = json.loads(line[6:])
            if event['type'] == 'error':
                raise RuntimeError(event['message'])
            if event['type'] == 'chunk':
                chunks.append(base64.b64decode(event['audio_b64']))
            if event['type'] == 'done':
                metrics = event['metrics']
        if not chunks or metrics is None:
            raise RuntimeError('Incomplete stream.')
        output = io.BytesIO()
        with wave.open(io.BytesIO(chunks[0]), 'rb') as first:
            parameters = first.getparams()
        with wave.open(output, 'wb') as combined:
            combined.setparams(parameters)
            for chunk in chunks:
                with wave.open(io.BytesIO(chunk), 'rb') as reader:
                    combined.writeframes(reader.readframes(reader.getnframes()))
        return output.getvalue(), metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:7860')
    parser.add_argument('--asr-url', default=os.getenv('QWEN_STUDIO_ASR_URL', ''),
                        help='Existing ASR service URL; defaults to QWEN_STUDIO_ASR_URL.')
    parser.add_argument('--output', type=Path, default=Path('artifacts/studio-smoke'))
    parser.add_argument('--all-models', action='store_true')
    args = parser.parse_args()
    args.asr_url = args.asr_url.strip().rstrip('/')
    if not re.match(r'^https?://[^\s]+$', args.asr_url):
        parser.error('Set --asr-url or QWEN_STUDIO_ASR_URL to an existing ASR service URL.')
    args.output.mkdir(parents=True, exist_ok=True)
    cases = [('custom', '0.6B-CustomVoice', False, True), ('design', '1.7B-VoiceDesign', False, True),
             ('clone', '0.6B-Base', False, True), ('clone', '0.6B-Base', False, False),
             ('clone', '0.6B-Base', True, True), ('custom', '0.6B-CustomVoice', True, True),
             ('design', '1.7B-VoiceDesign', True, True)]
    if args.all_models:
        cases += [('custom', '1.7B-CustomVoice', False, True), ('clone', '1.7B-Base', True, False)]
    reference, results = None, []
    for mode, model, streaming, identity_only in cases:
        options = {'mode': mode, 'model': 'Qwen/Qwen3-TTS-12Hz-' + model, 'text': TEXT,
                   'speaker': 'Ryan', 'language': 'English', 'seed': 42, 'max_new_tokens': 180,
                   'xvec_only': identity_only, 'ref_text': TEXT if mode == 'clone' else ''}
        if mode == 'design' or model == '1.7B-CustomVoice':
            options['instruct'] = 'A warm, clear narrator speaking naturally and calmly.'
        name = f'{model}-{"stream" if streaming else "complete"}-{"identity" if identity_only else "transcript"}'
        print('Generating', name, flush=True)
        audio, metrics = generate(args.base_url, options, reference if mode == 'clone' else None, streaming)
        (args.output / (name + '.wav')).write_bytes(audio)
        if reference is None:
            reference = audio
        with post(args.asr_url + '/v1/audio/transcriptions', {'model': 'qwen3-asr', 'response_format': 'json'},
                  {'file': ('generated.wav', audio)}) as response:
            transcript = json.load(response)['text']
        result = {'case': name, 'expected': TEXT, 'transcript': transcript,
                  'word_error_rate': round(word_error(TEXT, transcript), 4), 'metrics': metrics}
        results.append(result)
        print(json.dumps(result), flush=True)
        (args.output / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    if any(result['word_error_rate'] > .35 for result in results):
        raise SystemExit('Some samples require review: ASR word error rate exceeded 35%.')
    print(f'PASS: {len(results)} real generation/transcription cases')


if __name__ == '__main__':
    main()
