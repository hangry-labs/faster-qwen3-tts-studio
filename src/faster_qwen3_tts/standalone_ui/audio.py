"""Bounded audio effects, dialogue boundaries and single-pass encoding.

Dialogue boundary policy adapted from Hangry Labs VoxCPMTTS (Apache-2.0).
"""
from __future__ import annotations

import io
import subprocess
import tempfile
import threading

import numpy as np
import soundfile as sf

RATE = 24000
FORMATS = {
    'wav': ('audio/wav', 'wav', 'pcm_s16le'),
    'mp3': ('audio/mpeg', 'mp3', 'libmp3lame'),
    'flac': ('audio/flac', 'flac', 'flac'),
    'ogg': ('audio/ogg', 'ogg', 'libvorbis'),
    'opus': ('audio/ogg', 'ogg', 'libopus'),
    'aac': ('audio/aac', 'adts', 'aac'),
    'pcm': ('audio/pcm', 's16le', 'pcm_s16le'),
}


def pcm(audio):
    return (np.clip(audio, -1, 1) * 32767).astype('<i2').tobytes()


def wav(audio, rate=RATE):
    output = io.BytesIO()
    sf.write(output, audio, rate, format='WAV', subtype='PCM_16')
    return output.getvalue()


def tempo_filters(rate):
    filters = []
    while rate > 2:
        filters.append('atempo=2')
        rate /= 2
    while rate < .5:
        filters.append('atempo=0.5')
        rate /= .5
    return filters + [f'atempo={rate:.8f}']


def effects(audio, *, rate=1., pitch=0., volume=1., normalize=False):
    filters = []
    if pitch:
        factor = 2 ** (pitch / 12)
        filters += [f'asetrate={round(RATE * factor)}', f'aresample={RATE}']
        filters += tempo_filters(1 / factor)
    if rate != 1:
        filters += tempo_filters(rate)
    if volume != 1:
        filters.append(f'volume={volume:.8f}')
    if normalize:
        filters += ['loudnorm=I=-16:TP=-1.5:LRA=11', f'aresample={RATE}']
    if not filters or not len(audio):
        return audio
    process = subprocess.run(
        ['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(RATE), '-ac', '1',
         '-i', 'pipe:0', '-af', ','.join(filters), '-f', 'f32le', '-ar', str(RATE), 'pipe:1'],
        input=np.asarray(audio, dtype='<f4').tobytes(), capture_output=True, timeout=90)
    if process.returncode:
        raise RuntimeError('Audio processing failed: ' + process.stderr.decode(errors='replace')[-1000:])
    return np.frombuffer(process.stdout, dtype='<f4').copy()


def trim_internal(audio, leading):
    scan = min(len(audio), round(RATE * .6))
    if not scan:
        return audio
    section = audio[:scan] if leading else audio[-scan:]
    active = np.flatnonzero(np.abs(section) > 192 / 32768)
    if not len(active):
        return audio
    keep = round(RATE * .035)
    if leading:
        return audio[max(0, int(active[0]) - keep):]
    trim = max(0, scan - int(active[-1]) - 1 - keep)
    return audio[:-trim] if trim else audio


def assemble(items):
    """Yield ordered arrays, preserving outer edges and exact explicit gaps."""
    pending, gap, leading = None, None, 0
    for kind, value in items:
        if kind == 'break':
            if pending is None:
                leading += value
            else:
                gap = (gap or 0) + value
            continue
        current = np.asarray(value, dtype=np.float32)
        if pending is None:
            if leading:
                yield np.zeros(round(RATE * leading / 1000), dtype=np.float32)
                leading = 0
        else:
            yield trim_internal(pending, False)
            current = trim_internal(current, True)
            pause = gap if gap is not None else 120
            if pause:
                yield np.zeros(round(RATE * pause / 1000), dtype=np.float32)
        pending, gap = current, None
    if pending is not None:
        yield pending
        if gap:
            yield np.zeros(round(RATE * gap / 1000), dtype=np.float32)
    elif leading:
        yield np.zeros(round(RATE * leading / 1000), dtype=np.float32)


def encode(audio, fmt):
    if fmt == 'wav':
        return wav(audio)
    if fmt == 'flac':
        output = io.BytesIO()
        sf.write(output, audio, RATE, format='FLAC', subtype='PCM_16')
        return output.getvalue()
    if fmt == 'pcm':
        return pcm(audio)
    _, container, codec = FORMATS[fmt]
    process = subprocess.run(
        ['ffmpeg', '-v', 'error', '-f', 's16le', '-ar', str(RATE), '-ac', '1', '-i', 'pipe:0',
         '-c:a', codec, '-f', container, 'pipe:1'], input=pcm(audio), capture_output=True, timeout=90)
    if process.returncode:
        raise RuntimeError('Audio encoding failed: ' + process.stderr.decode(errors='replace')[-1000:])
    return process.stdout


def encode_stream(chunks, fmt, cancelled):
    """One encoder for a whole progressive response; never concatenate files."""
    if fmt == 'pcm':
        for chunk in chunks:
            if cancelled.is_set():
                return
            yield pcm(chunk)
        return
    _, container, codec = FORMATS[fmt]
    errors = []
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen(
            ['ffmpeg', '-v', 'error', '-f', 's16le', '-ar', str(RATE), '-ac', '1', '-i', 'pipe:0',
             '-c:a', codec, '-flush_packets', '1', '-f', container, 'pipe:1'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)

        def feed():
            try:
                for chunk in chunks:
                    if cancelled.is_set():
                        break
                    process.stdin.write(pcm(chunk))
            except Exception as exc:
                errors.append(exc)
            finally:
                try:
                    process.stdin.close()
                except OSError:
                    pass

        writer = threading.Thread(target=feed, daemon=True, name='qwen-audio-encoder')
        writer.start()
        try:
            while data := process.stdout.read1(8192):
                yield data
            writer.join(timeout=5)
            code = process.wait(timeout=15)
            if errors:
                raise errors[0]
            if code and not cancelled.is_set():
                raise RuntimeError('Streaming audio encoding failed.')
        finally:
            if process.poll() is None:
                cancelled.set()
                process.terminate()
            process.stdout.close()
            writer.join(timeout=5)
            process.wait(timeout=15)
