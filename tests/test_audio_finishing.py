"""Real CPU finishing preserves float audio and validates bounded mastering."""
import io
import json

from fastapi.testclient import TestClient
import numpy as np
import pytest
import soundfile as sf

from faster_qwen3_tts.standalone_ui import audio
from faster_qwen3_tts.standalone_ui.api import EffectsRequest
from faster_qwen3_tts.standalone_ui.finishing import finish_audio
from faster_qwen3_tts.standalone_ui.server import create_app


@pytest.mark.parametrize('method', ['signalsmith', 'ffmpeg-shape'])
def test_pitch_and_speed_shape_the_signal_independently(method):
    signal = .2 * np.sin(2 * np.pi * 220 * np.arange(audio.RATE * 2) / audio.RATE).astype(np.float32)
    processed = finish_audio(signal, EffectsRequest(method=method, pitch_semitones=6, speed_factor=1.25,
        deesser_strength_percent=0))
    assert 1.4 < len(processed) / audio.RATE < 1.8
    dominant = np.argmax(np.abs(np.fft.rfft(processed))) * audio.RATE / len(processed)
    assert 300 < dominant < 325
    assert np.isfinite(processed).all()


def test_advanced_mastering_with_normalization_and_float_wav(tmp_path):
    class Engine:
        def status(self):
            return {'state': 'idle'}
    signal = .25 * np.sin(2 * np.pi * 220 * np.arange(audio.RATE * 2) / audio.RATE).astype(np.float32)
    config = {'high_pass_hz': 70, 'warmth_db': 2, 'warmth_hz': 150, 'mud_db': -2, 'mud_hz': 300,
        'presence_hz': 3300, 'presence_db': 1, 'air_db': 1, 'air_hz': 9000,
        'compression_ratio': 2, 'compression_threshold_dbfs': -20, 'compression_attack_ms': 10,
        'compression_release_ms': 100, 'deesser_strength_percent': 15, 'saturation_blend_percent': 3,
        'room_percent': 2, 'target_loudness_lufs': -18, 'peak_ceiling_dbtp': -2, 'normalize_loudness': True}
    with TestClient(create_app(Engine(), tmp_path)) as client:
        result = client.post('/tts/postprocess-upload', data={'options': json.dumps(config)},
            files={'audio': ('source.wav', audio.wav(signal), 'audio/wav')})
    assert result.status_code == 200, result.text
    info = sf.info(io.BytesIO(result.content))
    assert info.subtype == 'FLOAT' and info.samplerate == audio.RATE
    output, rate = sf.read(io.BytesIO(result.content))
    assert np.isfinite(output).all() and np.max(np.abs(output)) < 1


@pytest.mark.parametrize('field,value', [('high_pass_hz', 151), ('air_hz', 14000),
    ('room_percent', 11), ('compression_ratio', 6), ('peak_ceiling_dbtp', 0), ('warmth_db', float('nan'))])
def test_invalid_mastering_is_rejected_before_processing(field, value):
    with pytest.raises(ValueError):
        EffectsRequest.model_validate({field: value})
