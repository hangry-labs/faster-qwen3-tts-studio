"""Bounded audio effects, dialogue boundaries and single-pass encoding.

Dialogue boundary policy adapted from Hangry Labs VoxCPMTTS (Apache-2.0).
"""
from __future__ import annotations

import io
import subprocess
import tempfile
import threading
import time

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


def effect_filters(*, rate=1., pitch=0., volume=1., normalize=False,
            noise=0., bass=0., presence=0., dynamics=0.):
    filters = []
    if pitch:
        factor = 2 ** (pitch / 12)
        filters += [f'asetrate={round(RATE * factor)}', f'aresample={RATE}']
        filters += tempo_filters(1 / factor)
    if rate != 1:
        filters += tempo_filters(rate)
    if volume != 1:
        filters.append(f'volume={volume:.8f}')
    if noise:
        filters.append(f'afftdn=nr={noise:.4f}:nf=-50')
    if bass:
        filters.append(f'bass=g={bass:.4f}:f=160:w=0.6')
    if presence:
        filters.append(f'equalizer=f=3000:t=q:w=1:g={presence:.4f}')
    if dynamics:
        filters.append(f'acompressor=threshold=0.125:ratio={1 + dynamics / 25:.4f}:attack=20:release=180:makeup=1')
    if normalize:
        filters += ['loudnorm=I=-16:TP=-1.5:LRA=11', f'aresample={RATE}']
    return filters


def effects(audio, *, rate=1., pitch=0., volume=1., normalize=False,
            noise=0., bass=0., presence=0., dynamics=0.):
    filters = effect_filters(rate=rate, pitch=pitch, volume=volume, normalize=normalize,
                             noise=noise, bass=bass, presence=presence, dynamics=dynamics)
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


class UnitBoundary:
    """Compact one unit incrementally, retaining only its 600 ms edge window."""

    def __init__(self, emit, *, leading, trailing):
        self.emit = emit
        self.leading = leading
        self.trailing = trailing
        self.window = round(RATE * .6)
        self.head = np.empty(0, dtype=np.float32)
        self.tail = np.empty(0, dtype=np.float32)

    def feed(self, samples):
        samples = np.asarray(samples, dtype=np.float32)
        if not len(samples):
            return
        if self.leading:
            self.head = np.concatenate((self.head, samples))
            if len(self.head) < self.window and not np.any(np.abs(self.head) > 192 / 32768):
                return
            samples = trim_internal(self.head, True)
            self.head = np.empty(0, dtype=np.float32)
            self.leading = False
        if self.trailing:
            self.tail = np.concatenate((self.tail, samples))
            if len(self.tail) > self.window:
                self.emit(self.tail[:-self.window])
                self.tail = self.tail[-self.window:]
        else:
            self.emit(samples)

    def finish(self):
        if self.leading:
            self.leading = False
            samples, self.head = trim_internal(self.head, True), np.empty(0, dtype=np.float32)
            self.feed(samples)
        if self.trailing:
            samples, self.tail = trim_internal(self.tail, False), np.empty(0, dtype=np.float32)
            if len(samples):
                self.emit(samples)


class StreamingFilter:
    """Feed float audio on the inference thread; drain one continuous filter."""

    def __init__(self, emit, cancelled, filters):
        self.emit, self.cancelled = emit, cancelled
        self.errors = []
        self.log = tempfile.TemporaryFile()
        try:
            self.process = subprocess.Popen(
                ['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(RATE), '-ac', '1',
                 '-probesize', '32', '-analyzeduration', '1', '-i', 'pipe:0', '-af', filters,
                 '-f', 'f32le', '-ar', str(RATE), 'pipe:1'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log)
        except BaseException:
            self.log.close()
            raise
        self.reader = threading.Thread(target=self._read, daemon=True, name='qwen-audio-filter')
        self.reader.start()

    def _read(self):
        pending = b''
        try:
            while data := self.process.stdout.read1(8192):
                if self.cancelled.is_set():
                    if self.process.poll() is None:
                        self.process.kill()
                    return
                pending += data
                end = len(pending) // 4 * 4
                if end:
                    self.emit(np.frombuffer(pending[:end], dtype='<f4').copy())
                    pending = pending[end:]
            if pending:
                raise RuntimeError('Audio filter returned an incomplete sample.')
        except Exception as exc:
            self.errors.append(exc)
            if self.process.poll() is None:
                self.process.kill()

    def feed(self, samples):
        if self.errors:
            raise self.errors[0]
        if self.cancelled.is_set():
            raise InterruptedError('Generation cancelled.')
        try:
            self.process.stdin.write(np.asarray(samples, dtype='<f4').tobytes())
            self.process.stdin.flush()
        except (BrokenPipeError, OSError):
            if self.errors:
                raise self.errors[0]
            raise RuntimeError('Audio filtering stopped before completion.') from None

    def __enter__(self):
        return self

    def __exit__(self, kind, error, traceback):
        process = self.process
        try:
            if self.cancelled.is_set() and process.poll() is None:
                process.kill()
            elif kind is not None and process.poll() is None:
                process.terminate()
            try:
                process.stdin.close()
            except (OSError, BrokenPipeError):
                pass
            deadline = time.monotonic() + 30
            while self.reader.is_alive() and time.monotonic() < deadline:
                self.reader.join(.1)
                if self.cancelled.is_set() and process.poll() is None:
                    process.terminate()
            if self.reader.is_alive():
                raise RuntimeError('Audio filter did not finish.')
            try:
                code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                code = process.wait(timeout=5)
                if kind is None and not self.cancelled.is_set():
                    raise RuntimeError('Audio filter did not exit.') from None
            if kind is None and not self.cancelled.is_set():
                if self.errors:
                    raise self.errors[0]
                if code:
                    self.log.seek(0)
                    raise RuntimeError('Audio filtering failed: ' + self.log.read().decode(errors='replace')[-1000:])
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            process.stdout.close()
            self.log.close()


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
            ['ffmpeg', '-v', 'error', '-f', 's16le', '-ar', str(RATE), '-ac', '1',
             '-probesize', '32', '-analyzeduration', '1', '-i', 'pipe:0',
             '-c:a', codec, '-flush_packets', '1', '-f', container, 'pipe:1'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)

        def feed():
            try:
                for chunk in chunks:
                    if cancelled.is_set():
                        break
                    process.stdin.write(pcm(chunk))
                    process.stdin.flush()
            except Exception as exc:
                errors.append(exc)
            finally:
                try:
                    process.stdin.close()
                except OSError:
                    pass

        writer = threading.Thread(target=feed, daemon=True, name='qwen-audio-encoder')
        stopped = threading.Event()
        def watch_cancel():
            while not stopped.wait(.1):
                if cancelled.is_set():
                    if process.poll() is None:
                        process.kill()
                    return
        watcher = threading.Thread(target=watch_cancel, daemon=True, name='qwen-audio-cancel')
        writer.start()
        watcher.start()
        try:
            while data := process.stdout.read1(8192):
                yield data
            writer.join(timeout=5)
            code = process.wait(timeout=15)
            if errors:
                if not cancelled.is_set():
                    raise errors[0]
            if code and not cancelled.is_set():
                raise RuntimeError('Streaming audio encoding failed.')
        finally:
            stopped.set()
            if process.poll() is None:
                cancelled.set()
                process.kill()
            process.stdout.close()
            writer.join(timeout=5)
            watcher.join(timeout=1)
            process.wait(timeout=5)
