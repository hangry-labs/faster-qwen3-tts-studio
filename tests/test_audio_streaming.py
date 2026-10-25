"""Incremental output preserves dialogue boundaries and real encoded samples."""
from contextlib import contextmanager
import io
import threading

import numpy as np
import pytest
import soundfile as sf

from faster_qwen3_tts.standalone_ui import audio
from faster_qwen3_tts.standalone_ui.profiles import VoiceStore
from faster_qwen3_tts.standalone_ui.speech import SpeechRequest, SpeechService


@pytest.mark.parametrize('leading,trailing', [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize('chunk_size', [1, 719, 8000, 60000])
def test_incremental_boundary_matches_complete_boundary(leading, trailing, chunk_size):
    source = np.r_[np.zeros(8000), np.full(18000, .2), np.zeros(8000)].astype(np.float32)
    expected = audio.trim_internal(source, True) if leading else source
    expected = audio.trim_internal(expected, False) if trailing else expected
    parts = []
    boundary = audio.UnitBoundary(parts.append, leading=leading, trailing=trailing)
    for offset in range(0, len(source), chunk_size):
        boundary.feed(source[offset:offset + chunk_size])
    boundary.finish()
    assert np.array_equal(np.concatenate(parts), expected)


def test_first_turn_streams_before_its_generation_and_next_turn_complete(tmp_path):
    order = []
    class Engine:
        @contextmanager
        def session(self, cancelled, emit):
            yield

        def generate(self, request, reference, cancelled, emit, streaming):
            assert streaming
            order.append('start:' + request.text)
            for _ in range(4):
                emit({'type': 'chunk', 'audio': np.full(8000, .2, dtype=np.float32), 'sample_rate': audio.RATE})
            order.append('end:' + request.text)
            emit({'type': 'done', 'metrics': {}})

    service = SpeechService(Engine(), VoiceStore(tmp_path))
    payload = SpeechRequest(text='<speak>First.<break time="0ms"/>Second.</speak>', input_type='ssml')
    def emit(event):
        if event['type'] == 'chunk':
            order.append('audio')
    result = service.run(service.prepare(payload), threading.Event(), emit, streaming=True)
    assert order.index('audio') < order.index('end:First.') < order.index('start:Second.')
    assert len(result['audio']) == 64000


def test_stream_normalization_uses_one_continuous_filter_and_matches_full_audio():
    time_axis = np.arange(audio.RATE * 6, dtype=np.float32) / audio.RATE
    source = .2 * np.sin(2 * np.pi * 220 * time_axis)
    parts = []
    received = threading.Event()
    def emit(samples):
        parts.append(samples)
        received.set()
    with audio.StreamingFilter(emit, threading.Event(), 'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=24000') as normalizer:
        for offset in range(0, len(source), 4000):
            normalizer.feed(source[offset:offset + 4000])
            if offset == 120000:
                assert received.wait(3), 'Normalized audio should arrive before the source ends'
    actual = np.concatenate(parts)
    expected = audio.effects(source, normalize=True)
    assert len(actual) == len(expected)
    assert np.allclose(actual, expected, atol=1e-6)


def test_filter_error_cleans_up_process_and_is_not_a_success():
    cancelled = threading.Event()
    with pytest.raises(RuntimeError, match='Audio filter|Audio filtering'):
        with audio.StreamingFilter(lambda samples: None, cancelled, 'not_a_real_filter') as processor:
            processor.feed(np.ones(24000, dtype=np.float32))
    assert processor.process.poll() is not None


def test_cancelling_filter_releases_reader_and_process():
    cancelled = threading.Event()
    with audio.StreamingFilter(lambda samples: None, cancelled, 'volume=0.5') as processor:
        processor.feed(np.ones(24000, dtype=np.float32))
        cancelled.set()
    assert processor.process.poll() is not None
    assert not processor.reader.is_alive()


def test_mp3_sends_audio_packets_before_the_source_is_finished():
    delivered = threading.Event()
    def source():
        yield np.full(24000, .2, dtype=np.float32)
        assert delivered.wait(5), 'Encoder buffered its first second until source EOF'
        yield np.full(24000, .2, dtype=np.float32)
    chunks, count = [], 0
    for data in audio.encode_stream(source(), 'mp3', threading.Event()):
        chunks.append(data); count += len(data)
        # More than the tiny ID3 header: complete MPEG audio frames are present.
        if count > 1024:
            delivered.set()
    assert delivered.is_set() and sum(map(len, chunks)) > 2048


@pytest.mark.parametrize('fmt', ['mp3', 'opus', 'aac', 'ogg', 'flac', 'pcm'])
def test_low_latency_encoding_produces_complete_decodable_audio(fmt):
    import subprocess
    samples = np.sin(2 * np.pi * 220 * np.arange(24000) / audio.RATE).astype(np.float32) * .2
    result = b''.join(audio.encode_stream((samples[offset:offset + 1000] for offset in range(0, len(samples), 1000)),
                                        fmt, threading.Event()))
    if fmt == 'pcm':
        assert result == audio.pcm(samples)
    else:
        decoded = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'pipe:0', '-f', 'f32le',
                                  '-ar', '24000', '-ac', '1', 'pipe:1'], input=result, capture_output=True, check=True)
        wave = np.frombuffer(decoded.stdout, dtype='<f4')
        assert abs(len(wave) - len(samples)) < 2400
        assert np.isfinite(wave).all() and np.max(np.abs(wave)) > .1
