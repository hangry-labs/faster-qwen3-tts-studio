# SPDX-License-Identifier: Apache-2.0
# Mastering filters adapted from Hangry Labs VoxCPMTTS.
"""Non-destructive finishing at Qwen's native sample rate."""
import subprocess

import numpy as np

from . import audio

def build_filters(payload):
    filters = [f"highpass=f={payload.high_pass_hz:g}:p=2"]
    if payload.noise_reduction_db > 0:
        filters.append(f"afftdn=nr={payload.noise_reduction_db:g}:nf=-50:tn=1:gs=6")
    warmth_gain = payload.warmth_db if payload.warmth_db is not None else payload.bass_db
    warmth_frequency = payload.warmth_hz if payload.warmth_hz is not None else 110.0
    if payload.warmth_db is None and payload.bass_db:
        filters.append(f"bass=f=110:t=q:w=0.7:g={payload.bass_db:g}:p=2:r=f32")
    elif warmth_gain:
        filters.append(f"equalizer=f={warmth_frequency:g}:t=q:w=0.8:g={warmth_gain:g}:r=f32")
    if payload.mud_db:
        filters.append(f"equalizer=f={payload.mud_hz:g}:t=q:w=1:g={payload.mud_db:g}:r=f32")
    if payload.presence_db:
        if payload.presence_hz is None:
            filters.append(f"treble=f=3500:t=q:w=0.7:g={payload.presence_db:g}:p=2:r=f32")
        else:
            filters.append(f"equalizer=f={payload.presence_hz:g}:t=q:w=0.8:g={payload.presence_db:g}:r=f32")
    if payload.air_db:
        filters.append(f"treble=f={payload.air_hz:g}:t=q:w=0.7:g={payload.air_db:g}:p=2:r=f32")
    if payload.compression_ratio is not None and payload.compression_ratio > 1:
        threshold = 10 ** (payload.compression_threshold_dbfs / 20.0)
        filters.append(
            f"acompressor=threshold={threshold:.6f}:ratio={payload.compression_ratio:g}:"
            f"attack={payload.compression_attack_ms:g}:release={payload.compression_release_ms:g}:"
            "knee=2.828:makeup=1:mix=1"
        )
    elif payload.dynamics:
        wet_mix = payload.dynamics / 100.0
        filters.append(
            "acompressor=threshold=0.125:ratio=2:attack=20:release=250:"
            f"knee=2.828:makeup=1.15:mix={wet_mix:g}"
        )
    deesser = 12.0 if payload.deesser_strength_percent is None else payload.deesser_strength_percent
    if deesser > 0:
        filters.append(f"deesser=i={deesser / 100.0:g}:m=0.35:f=0.5")
    if payload.saturation_blend_percent > 0:
        threshold = max(0.55, 1.0 - payload.saturation_blend_percent / 45.0)
        filters.append(f"asoftclip=type=tanh:threshold={threshold:g}:output=1:oversample=4")
    if payload.room_percent > 0:
        decay = payload.room_percent / 100.0
        filters.append(f"aecho=in_gain=0.9:out_gain=1:delays=28:decays={decay:g}")
    peak_limit = 10 ** (payload.peak_ceiling_dbtp / 20.0)
    filters.append(f"alimiter=limit={peak_limit:.3f}:attack=5:release=50:level=disabled")
    if payload.normalize_loudness:
        filters.append(
            f"loudnorm=I={payload.target_loudness_lufs:g}:"
            f"TP={payload.peak_ceiling_dbtp:g}:LRA=11"
        )
    return ",".join(filters)


def finish_audio(samples, config):
    shape = config.method in {'signalsmith', 'ffmpeg-shape'}
    pitch = config.pitch_semitones if shape and config.pitch_semitones is not None else config.pitch
    speed = config.speed_factor if shape and config.speed_factor is not None else config.speed
    if config.method == 'signalsmith' and (pitch or speed != 1):
        import python_stretch
        processor = python_stretch.Signalsmith.Stretch(0)
        processor.preset(1, audio.RATE)
        processor.setTransposeSemitones(float(pitch), 8000 / audio.RATE)
        processor.timeFactor = float(speed)
        samples = np.asarray(processor.process(np.ascontiguousarray(samples[None, :], dtype=np.float32)))
        if samples.ndim != 2 or samples.shape[0] != 1 or samples.shape[1] == 0:
            raise RuntimeError('Signalsmith returned an invalid audio buffer.')
        samples = samples[0]
        if not np.isfinite(samples).all():
            raise RuntimeError('Signalsmith returned non-finite audio.')
        samples = audio.effects(samples, volume=config.volume)
    else:
        samples = audio.effects(samples, rate=speed, pitch=pitch, volume=config.volume)
    if len(samples) > audio.RATE * 300:
        raise ValueError('Processed audio exceeds the 300 second output limit.')
    process = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(audio.RATE), '-ac', '1',
        '-i', 'pipe:0', '-af', build_filters(config), '-ar', str(audio.RATE), '-f', 'f32le', 'pipe:1'],
        input=np.asarray(samples, dtype='<f4').tobytes(), capture_output=True, timeout=90)
    if process.returncode:
        raise RuntimeError('Audio finishing failed: ' + process.stderr.decode(errors='replace')[-1000:])
    result = np.frombuffer(process.stdout, dtype='<f4').copy()
    if not len(result) or len(result) > audio.RATE * 300 or not np.isfinite(result).all():
        raise ValueError('Processed audio must be finite and no longer than 300 seconds.')
    return result
