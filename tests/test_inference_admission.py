"""Bounded admission protects real HTTP boundaries, FIFO order and cancellation."""
import json
import threading
from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest

from faster_qwen3_tts.standalone_ui.runtime import (
    InferenceQueueFull, StudioEngine, start_request_thread,
)
from faster_qwen3_tts.standalone_ui.server import create_app


def test_reservations_are_bounded_before_threads_start_and_capacity_is_reusable():
    engine = StudioEngine(queue_capacity=1)
    first, second = engine.admit(), engine.admit()
    with pytest.raises(InferenceQueueFull):
        engine.admit()
    assert engine.status()['queue']['rejected'] == 1
    engine.cancel_admission(second)
    replacement = engine.admit()
    engine.cancel_admission(first)
    engine.cancel_admission(replacement)
    assert engine.status()['queue_depth'] == 0


def test_zero_waiting_slots_still_allows_one_idle_request():
    engine = StudioEngine(queue_capacity=0)
    ticket = engine.admit()
    with engine.admitted(ticket):
        assert engine._acquire(threading.Event(), lambda event: None)
        try:
            with pytest.raises(InferenceQueueFull):
                engine.admit()
        finally:
            engine.gate.release()
    assert not engine.waiters


def test_cancelled_reservation_does_not_leak_or_overtake_a_preceding_request():
    engine = StudioEngine(queue_capacity=2)
    first, second = engine.admit(), engine.admit()
    positions = []
    cancelled = threading.Event(); cancelled.set()
    with engine.admitted(second):
        assert not engine._acquire(cancelled, positions.append)
    with engine.admitted(first):
        assert engine._acquire(threading.Event(), positions.append)
        engine.gate.release()
    assert positions == [{'type': 'queued', 'position': 0}]
    assert not engine.waiters


def test_thread_start_failure_releases_reserved_capacity():
    engine = StudioEngine(queue_capacity=0)
    with patch('threading.Thread.start', side_effect=RuntimeError('cannot start')):
        with pytest.raises(RuntimeError, match='cannot start'):
            start_request_thread(engine, lambda: None, name='admission-test')
    assert not engine.waiters
    engine.cancel_admission(engine.admit())


@pytest.mark.parametrize('capacity', [-1, 257, True, 'bad', 1.5])
def test_invalid_capacity_is_actionable(capacity):
    with pytest.raises(ValueError, match='integer from 0 to 256'):
        StudioEngine(queue_capacity=capacity)


@pytest.mark.parametrize('route,payload', [
    ('/tts/generate', {'text': 'Hello'}),
    ('/tts/stream', {'text': 'Hello', 'stream_format': 'pcm'}),
    ('/tts/events', {'text': 'Hello'}),
    ('/v1/audio/speech', {'model': 'qwen3-tts', 'input': 'Hello', 'voice': 'Ryan'}),
    ('/studio/generate', None),
    ('/studio/generate/stream', None),
])
def test_full_queue_returns_429_before_any_worker_or_stream(route, payload, tmp_path):
    engine = StudioEngine(queue_capacity=0)
    ticket = engine.admit()
    try:
        with TestClient(create_app(engine, tmp_path)) as client, patch.object(engine, 'generate') as generate, \
                patch('faster_qwen3_tts.standalone_ui.speech.SpeechService.prepare') as prepare:
            response = client.post(route, json=payload) if payload else client.post(route,
                data={'options': json.dumps({'text': 'Hello'})})
            assert response.status_code == 429, response.text
            assert response.headers['Retry-After'] == '1'
            if route.startswith('/v1'):
                assert response.json()['error']['type'] == 'rate_limit_error'
            else:
                assert response.json()['code'] == 'inference_queue_full'
            generate.assert_not_called()
            if not route.startswith('/studio/'):
                prepare.assert_not_called()
    finally:
        engine.cancel_admission(ticket)
