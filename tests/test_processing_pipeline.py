"""Scheduling proofs use barriers rather than timing-based speed assertions."""
import threading
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

import numpy as np
import pytest

from faster_qwen3_tts.standalone_ui import audio
from faster_qwen3_tts.standalone_ui.profiles import VoiceStore
from faster_qwen3_tts.standalone_ui.runtime import InferenceQueueFull, StudioEngine
from faster_qwen3_tts.standalone_ui.speech import SpeechRequest, SpeechService, start_worker
from faster_qwen3_tts.standalone_ui.server import create_app


class Engine(StudioEngine):
    def __init__(self, **options):
        super().__init__(**options)
        self.calls = []
        self.second = threading.Event()

    def generate(self, config, reference, cancelled, emit, streaming):
        assert self.gate.locked() and self.session_owner.active
        self.calls.append(config.text)
        if len(self.calls) == 2:
            self.second.set()
        emit({'type': 'chunk', 'audio': np.full(2400, .1, dtype=np.float32), 'sample_rate': audio.RATE})
        emit({'type': 'done', 'metrics': {'model_load_ms': 0}})


def drain(events):
    result = None
    while True:
        event = events.get(timeout=5)
        assert event['type'] != 'error', event
        if event['type'] == 'result':
            result = event['result']
        if event['type'] == 'finished':
            join_workers()
            return result


def join_workers():
    # The final event can arrive just before the worker's admission context exits.
    for thread in threading.enumerate():
        if thread.name == 'qwen-speech-request':
            thread.join(timeout=5)
            assert not thread.is_alive()


def test_next_request_uses_gpu_while_previous_normalizes_and_capacity_stays_bounded(tmp_path):
    engine = Engine(queue_capacity=1)
    service = SpeechService(engine, VoiceStore(tmp_path))
    entered, release, both = threading.Event(), threading.Event(), threading.Event()
    count, lock = 0, threading.Lock()
    original = audio.effects

    def effects(samples, **options):
        nonlocal count
        if options.get('normalize'):
            assert not engine.session_owner.active
            with lock:
                count += 1
                if count == 2:
                    both.set()
            entered.set()
            assert release.wait(5)
        return original(samples, **options)

    with patch.object(audio, 'effects', effects):
        first, cancel_first = start_worker(service, service.prepare(SpeechRequest(text='First.', normalize_loudness=True)))
        second = cancel_second = None
        try:
            assert entered.wait(5)
            second, cancel_second = start_worker(service, service.prepare(SpeechRequest(text='Second.', normalize_loudness=True)))
            assert engine.second.wait(5), 'CPU finishing still owns the GPU'
            assert both.wait(5)
            assert engine.status()['queue']['inflight'] == 2
            with pytest.raises(InferenceQueueFull):
                start_worker(service, service.prepare(SpeechRequest(text='Overflow.')))
        finally:
            release.set()
        a, b = drain(first), drain(second)
    assert np.array_equal(a['audio'], b['audio'])
    assert a['metrics']['postprocess_ms'] > 0
    assert not engine.gate.locked()
    assert not engine.admissions


def test_next_unit_synthesizes_while_previous_unit_effect_is_pending(tmp_path):
    engine = Engine()
    service = SpeechService(engine, VoiceStore(tmp_path))
    entered, release = threading.Event(), threading.Event()
    original = audio.effects

    def effects(samples, **options):
        entered.set()
        assert release.wait(5)
        return original(samples, **options)

    prepared = service.prepare(SpeechRequest(input_type='ssml', text=(
        '<speak><prosody rate="110%">First.</prosody><break time="0ms"/>'
        '<prosody pitch="+2st">Second.</prosody></speak>')))
    with patch.object(audio, 'effects', effects):
        events, cancel = start_worker(service, prepared)
        try:
            assert entered.wait(5)
            assert engine.second.wait(5), 'CPU effects block the next GPU unit'
        finally:
            release.set()
        result = drain(events)
    assert list(result['takes']) == ['0', '1']
    assert engine.calls == ['First.', 'Second.']
    assert not engine.admissions and not engine.gate.locked()


def test_processing_error_releases_lease_and_reservation(tmp_path):
    engine = Engine(queue_capacity=0)
    service = SpeechService(engine, VoiceStore(tmp_path))
    with patch.object(audio, 'effects', side_effect=RuntimeError('processing failed')):
        events, _ = start_worker(service, service.prepare(SpeechRequest(text='Test.')))
        errors = []
        while True:
            event = events.get(timeout=5)
            if event['type'] == 'error':
                errors.append(event['message'])
            if event['type'] == 'finished':
                break
    assert errors == ['processing failed']
    join_workers()
    assert not engine.admissions and not engine.gate.locked()
    engine.cancel_admission(engine.admit())


def test_planning_runs_off_event_loop_and_invalid_input_returns_admission(tmp_path):
    engine = Engine(queue_capacity=0)
    entered, release = threading.Event(), threading.Event()
    original = SpeechService.prepare

    def prepare(service, *args, **options):
        entered.set()
        assert release.wait(5)
        return original(service, *args, **options)

    with TestClient(create_app(engine, tmp_path)) as client, patch.object(SpeechService, 'prepare', prepare), \
            ThreadPoolExecutor(max_workers=1) as executor:
        request = executor.submit(client.post, '/tts/generate', json={'text': '<speak><bad/></speak>', 'input_type': 'ssml'})
        try:
            assert entered.wait(5)
            # The ASGI loop still serves status and rejects over-capacity work
            # before attempting any more expensive planning.
            assert client.get('/tts/status').status_code == 200
            assert client.post('/tts/events', json={'text': 'Overflow.'}).status_code == 429
        finally:
            release.set()
        assert request.result(timeout=5).status_code == 422
    assert not engine.admissions and not engine.waiters


def test_cancelled_finishing_does_not_hold_gpu_or_leak_capacity(tmp_path):
    engine = Engine(queue_capacity=0)
    service = SpeechService(engine, VoiceStore(tmp_path))
    entered, release = threading.Event(), threading.Event()

    def effects(samples, **options):
        entered.set()
        assert release.wait(5)
        return samples

    with patch.object(audio, 'effects', effects):
        events, cancelled = start_worker(service, service.prepare(SpeechRequest(text='Cancel me.')))
        assert entered.wait(5)
        cancelled.set()
        release.set()
        # Cancelled workers intentionally stop writing to their event channel.
        join_workers()
    assert not engine.gate.locked() and not engine.admissions


def test_processed_benchmark_exercises_real_planner_controls(tmp_path):
    from benchmarks.supplemental import queue_payload
    from faster_qwen3_tts.standalone_ui.speech import CUSTOM
    service = SpeechService(Engine(), VoiceStore(tmp_path))
    request = SpeechRequest(**queue_payload(CUSTOM, 42, workload='processed'))
    prepared = service.prepare(request)
    units = [u for u in prepared.plan.units if u.kind == 'speech']
    assert request.normalize_loudness
    assert len(units) == 2
    assert units[0].prosody.rate == 1.1
    assert units[0].prosody.pitch_semitones == 2
    assert units[1].prosody.rate == .9 and units[1].prosody.volume < 1
    assert sum(u.duration_ms for u in prepared.plan.units if u.kind == 'break') == 120


def test_streaming_filter_tail_releases_gpu_before_draining(tmp_path):
    engine = Engine(queue_capacity=1)
    service = SpeechService(engine, VoiceStore(tmp_path))
    entered, release = threading.Event(), threading.Event()

    class Filter:
        def __init__(self, emit, *args):
            self.feed = emit

        def __enter__(self):
            return self

        def __exit__(self, *_):
            assert not engine.session_owner.active
            entered.set()
            assert release.wait(5)

    with patch.object(audio, 'StreamingFilter', Filter):
        first, _ = start_worker(service, service.prepare(SpeechRequest(text='First.', normalize_loudness=True)), streaming=True)
        second = None
        try:
            assert entered.wait(5)
            second, _ = start_worker(service, service.prepare(SpeechRequest(text='Second.')), streaming=True)
            assert engine.second.wait(5)
        finally:
            release.set()
        assert drain(first)['audio'].size
        assert drain(second)['audio'].size
    assert not engine.admissions and not engine.gate.locked()


def test_slow_preparation_keeps_fifo_order_without_blocking_http_loop(tmp_path):
    engine = Engine(queue_capacity=1)
    entered, second_ready, release = threading.Event(), threading.Event(), threading.Event()
    original = SpeechService.prepare

    def prepare(service, payload, *args):
        if payload.text == 'First.':
            entered.set()
            assert release.wait(5)
        prepared = original(service, payload, *args)
        if payload.text == 'Second.':
            second_ready.set()
        return prepared

    with TestClient(create_app(engine, tmp_path)) as client, patch.object(SpeechService, 'prepare', prepare), \
            ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(client.post, '/tts/generate', json={'text': 'First.'})
        assert entered.wait(5)
        second = executor.submit(client.post, '/tts/generate', json={'text': 'Second.'})
        try:
            assert second_ready.wait(5)
            assert not engine.calls
        finally:
            release.set()
        assert first.result(timeout=5).status_code == second.result(timeout=5).status_code == 200
    assert engine.calls == ['First.', 'Second.']
    join_workers()
    assert not engine.admissions and not engine.gate.locked()
