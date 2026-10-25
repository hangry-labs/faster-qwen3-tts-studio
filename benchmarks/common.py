"""Shared benchmark measurements adapted from Hangry Labs VoxCPMTTS (Apache-2.0).

Only the Python standard library is required on the host. See NOTICE.
"""
from __future__ import annotations
import difflib
import hashlib
import io
import json
import math
import os
import statistics
import subprocess
import threading
import time
import unicodedata
import urllib.error
import urllib.request
import uuid
import wave
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import base64
import re

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = ROOT / 'benchmark-artifacts'
def command(
    args: list[str],
    *,
    check: bool = True,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8',
                          errors='replace', check=check, timeout=timeout)


def docker(*args: str, check: bool = True, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return command(["docker", *args], check=check, timeout=timeout)


def request_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def gpu_snapshot(gpu_index: int) -> dict[str, Any] | None:
    args = [
        "nvidia-smi",
        f"--id={gpu_index}",
        "--query-gpu=index,name,driver_version,memory.total,memory.used,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = command(args, timeout=15)
        line = next(line for line in result.stdout.splitlines() if line.strip())
        index, name, driver, total, used, utilization = (part.strip() for part in line.split(",", 5))
        return {
            "index": int(index),
            "name": name,
            "driver": driver,
            "total_mib": int(total),
            "used_mib": int(used),
            "utilization_percent": int(utilization),
        }
    except (FileNotFoundError, StopIteration, subprocess.SubprocessError, ValueError):
        return None


class GpuSampler:
    def __init__(self, gpu_index: int, interval: float) -> None:
        self.gpu_index = gpu_index
        self.interval = interval
        self.samples: list[dict[str, Any]] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _sample(self) -> None:
        started = time.monotonic()
        snapshot = gpu_snapshot(self.gpu_index)
        if snapshot is not None:
            snapshot['sample_monotonic'] = started
            self.samples.append(snapshot)

    def _run(self) -> None:
        while not self._stop.is_set():
            self._sample()
            self._stop.wait(self.interval)
        self._sample()

    def __enter__(self) -> "GpuSampler":
        self._thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._stop.set()
        self._thread.join(timeout=15)
        if self._thread.is_alive():
            raise RuntimeError('GPU sampler did not stop; measurements are incomplete.')

    def summary(self, baseline_mib: int | None) -> dict[str, Any]:
        if not self.samples:
            return {"samples": 0, "peak_mib": None, "peak_delta_mib": None, "mean_utilization_percent": None}
        used = [int(item["used_mib"]) for item in self.samples]
        utilization = [int(item["utilization_percent"]) for item in self.samples]
        peak = max(used)
        return {
            "samples": len(self.samples),
            "poll_interval_requested_seconds": self.interval,
            "sample_span_seconds": self.samples[-1]['sample_monotonic'] - self.samples[0]['sample_monotonic'],
            "peak_mib": peak,
            "peak_delta_mib": peak - baseline_mib if baseline_mib is not None else None,
            "mean_utilization_percent": round(statistics.fmean(utilization), 1),
            "peak_utilization_percent": max(utilization),
        }


def image_metadata(image: str) -> dict[str, Any]:
    payload = json.loads(docker("image", "inspect", image, timeout=30).stdout)[0]
    return {
        "tag": image,
        "id": payload.get("Id"),
        "created": payload.get("Created"),
        "size_bytes": payload.get("Size"),
        "repo_digests": payload.get("RepoDigests") or [],
        "labels": (payload.get("Config") or {}).get("Labels") or {},
    }


def container_memory(container: str) -> dict[str, float | None]:
    script = "for f in memory.current memory.peak; do test -f /sys/fs/cgroup/$f && cat /sys/fs/cgroup/$f || echo 0; done"
    try:
        lines = docker("exec", container, "sh", "-c", script, timeout=30).stdout.splitlines()
        current, peak = (int(lines[index]) if index < len(lines) and lines[index].isdigit() else 0 for index in range(2))
        return {
            "current_mib": round(current / (1024 * 1024), 1) if current else None,
            "peak_mib": round(peak / (1024 * 1024), 1) if peak else None,
        }
    except (subprocess.SubprocessError, ValueError):
        return {"current_mib": None, "peak_mib": None}

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_transcript(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return "".join(character for character in normalized if unicodedata.category(character)[0] in {"L", "N"})


def similarity(expected: str, actual: str) -> float:
    left = normalize_transcript(expected)
    right = normalize_transcript(actual)
    if not left and not right:
        return 100.0
    return round(100.0 * difflib.SequenceMatcher(None, left, right).ratio(), 2)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def wav_duration(audio: bytes) -> tuple[float, int]:
    with wave.open(io.BytesIO(audio), "rb") as source:
        if source.getframerate() <= 0 or source.getnframes() <= 0 or source.getnchannels() != 1:
            raise ValueError('Expected nonempty mono WAV audio.')
        return source.getnframes() / source.getframerate(), source.getframerate()


def append_run(path: Path, run: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"schema": 1, "runs": []}
    data.setdefault("runs", []).append(run)
    data["latest"] = run
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return data


def summarize_calls(calls: list[dict[str, Any]]) -> dict[str, Any]:
    tts_good = [item for item in calls if "tts_seconds" in item]
    quality_good = [item for item in tts_good if "similarity_percent" in item]
    rtfs = [float(item["rtf"]) for item in tts_good]
    similarities = [float(item["similarity_percent"]) for item in quality_good]
    exact = sum(bool(item.get("exact")) for item in quality_good)
    gpu_peaks = [
        int(item["gpu"]["peak_delta_mib"])
        for item in tts_good
        if item.get("gpu", {}).get("peak_delta_mib") is not None
    ]
    total_tts_seconds = sum(float(item["tts_seconds"]) for item in tts_good)
    return {
        "calls": len(calls),
        "completed": len(tts_good),
        "quality_completed": len(quality_good),
        "tts_errors": len(calls) - len(tts_good),
        "asr_errors": len(tts_good) - len(quality_good),
        "errors": len(calls) - len(quality_good),
        "audio_seconds": round(sum(float(item["audio_seconds"]) for item in tts_good), 3),
        "tts_seconds": round(total_tts_seconds, 3),
        "rtf_median": round(statistics.median(rtfs), 4) if rtfs else None,
        "rtf_p95": round(percentile(rtfs, 0.95), 4) if rtfs else None,
        "realtime_speed": round(sum(float(item["audio_seconds"]) for item in tts_good) / total_tts_seconds, 2)
        if total_tts_seconds
        else None,
        "exact_percent": round(100 * exact / len(quality_good), 2) if quality_good else 0.0,
        "mean_similarity_percent": round(statistics.fmean(similarities), 2) if similarities else 0.0,
        "min_similarity_percent": round(min(similarities), 2) if similarities else 0.0,
        "gpu_peak_delta_mib": max(gpu_peaks) if gpu_peaks else None,
    }


def consistency(calls: list[dict[str, Any]]) -> tuple[int, int]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in calls:
        grouped[item["case_id"]].append(item)
    consistent = 0
    for values in grouped.values():
        transcripts = {item.get("transcript_normalized") for item in values if not item.get("error")}
        if len(values) > 1 and all(not item.get('error') for item in values) and len(transcripts) == 1 and None not in transcripts:
            consistent += 1
    repeated = sum(1 for values in grouped.values() if len(values) > 1)
    return consistent, repeated


def backend_summary(calls: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode = {mode: summarize_calls([item for item in calls if item["mode"] == mode]) for mode in sorted({item["mode"] for item in calls})}
    by_language = {
        language: summarize_calls([item for item in calls if item["language"] == language])
        for language in sorted({item["language"] for item in calls})
    }
    consistent, repeated = consistency(calls)
    return {
        "overall": summarize_calls(calls),
        "by_mode": by_mode,
        "by_language": by_language,
        "consistent_cases": consistent,
        "repeated_cases": repeated,
        "consistent_case_percent": round(100 * consistent / repeated, 2) if repeated else 0.0,
    }


def stable_seed(call_id):
    return int.from_bytes(hashlib.sha256(call_id.encode('utf-8')).digest()[:4], 'big')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def harness_metadata():
    files = [(path.relative_to(ROOT / 'benchmarks').as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
        for path in sorted((ROOT / 'benchmarks').rglob('*'))
        if path.suffix in {'.py', '.json'} and 'research' not in path.parts and path.name != 'runs.json']
    return {'sha256': fingerprint(files), 'files': dict(files)}


def safe_error(error):
    return re.sub(r'https?://[^\s]+', '[service]', f'{type(error).__name__}: {error}')[:1000]


def multipart(fields, files):
    boundary = 'QwenBenchmark' + uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for name, (filename, content) in files.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: audio/wav\r\n\r\n'.encode() + content + b'\r\n')
    return b''.join(parts) + f'--{boundary}--\r\n'.encode(), 'multipart/form-data; boundary=' + boundary


def generate(base_url, payload, *, reference=None, streaming=False, timeout=900, request_id=None):
    """Measure at the client; SSE TTFA is first decoded nonempty audio, not HTTP headers."""
    path = '/tts/events' if streaming else '/tts/generate'
    headers = {}
    if request_id:
        headers['X-Qwen-Request-ID'] = request_id
    if reference is None:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    elif streaming:
        # Native events are JSON only. Register the same fixed reference once,
        # outside measurements, then use voice_profile for streaming clones.
        raise ValueError('Streaming clones require a pre-registered voice_profile.')
    else:
        path = '/tts/generate-upload'
        body, headers['Content-Type'] = multipart({'payload': json.dumps(payload, ensure_ascii=False)},
            {'reference_audio': ('reference.wav', reference)})
    started = time.perf_counter()
    first = None
    arrivals = []
    server_metrics = {}
    with urllib.request.urlopen(urllib.request.Request(base_url + path, data=body, headers=headers), timeout=timeout) as response:
        returned = {key.lower(): value for key, value in response.headers.items()}
        if not streaming:
            audio = response.read()
            if not returned.get('content-type', '').startswith('audio/wav'):
                raise ValueError('Expected a WAV response.')
            server_metrics = json.loads(returned.get('x-qwen-metrics', '{}'))
        else:
            if not returned.get('content-type', '').startswith('text/event-stream'):
                raise ValueError('Expected audio events.')
            chunks, sample_rate, done = [], None, False
            # Product events currently contain one JSON data line per frame.
            for line in response:
                if not line.startswith(b'data: '):
                    continue
                event = json.loads(line[6:])
                if event['type'] == 'error':
                    raise RuntimeError(event['message'])
                if event['type'] == 'chunk':
                    chunk = base64.b64decode(event['audio_b64'], validate=True)
                    with wave.open(io.BytesIO(chunk), 'rb') as source:
                        if source.getnchannels() != 1 or source.getsampwidth() != 2 or not source.getnframes():
                            raise ValueError('Invalid streamed PCM WAV chunk.')
                        if sample_rate not in (None, source.getframerate()):
                            raise ValueError('Stream sample rate changed.')
                        sample_rate = source.getframerate()
                        chunks.append(source.readframes(source.getnframes()))
                    if first is None:
                        first = time.perf_counter() - started
                    arrivals.append({'arrival_ms': round((time.perf_counter() - started) * 1000, 3),
                        'audio_ms': round(source.getnframes() / sample_rate * 1000, 3)})
                elif event['type'] == 'done':
                    done = True; server_metrics = event.get('metrics', {})
            if not chunks or not done:
                raise RuntimeError('Audio stream ended before completion.')
            output = io.BytesIO()
            with wave.open(output, 'wb') as target:
                target.setnchannels(1); target.setsampwidth(2); target.setframerate(sample_rate)
                target.writeframes(b''.join(chunks))
            audio = output.getvalue()
    elapsed = time.perf_counter() - started
    response_seed = server_metrics.get('seed', returned.get('x-qwen-seed'))
    if response_seed is not None and int(response_seed) != payload.get('seed'):
        raise ValueError('Server did not honor the requested fixed seed.')
    duration, sample_rate = wav_duration(audio)
    return audio, {'tts_seconds': round(elapsed, 6), 'audio_seconds': round(duration, 6),
        'rtf': round(elapsed / duration, 6), 'bytes': len(audio), 'sample_rate': sample_rate,
        'sha256': hashlib.sha256(audio).hexdigest(), 'seed': payload.get('seed'),
        'client_ttfa_ms': round(first * 1000, 3) if first is not None else None,
        'stream_chunks': arrivals, 'stream_chunk_count': len(arrivals) if streaming else None,
        'max_chunk_gap_ms': max((b['arrival_ms'] - a['arrival_ms'] for a, b in zip(arrivals, arrivals[1:])), default=None),
        'first_audio_semantics': 'first decoded SSE audio chunk' if streaming else 'complete response; not streaming TTFA',
        'server_metrics': server_metrics, 'response_seed': int(response_seed) if response_seed is not None else None}


def asr_inventory(base_url):
    health = request_json('GET', base_url + '/health/ready')
    if health.get('ready') is False or health.get('status') in {'error', 'unavailable'}:
        raise RuntimeError('ASR service is not ready.')
    languages = request_json('GET', base_url + '/v1/audio/supported_languages')['languages']
    models = request_json('GET', base_url + '/v1/models')['data']
    if not models:
        raise ValueError('ASR service did not advertise a model.')
    return {'model': str(models[0]['id']), 'supported_languages': sorted(languages),
        'role': 'fixed comparative transcript judge, not ground truth'}


def transcribe(base_url, audio, language, filename):
    body, content_type = multipart({'model': 'qwen3-asr', 'response_format': 'verbose_json',
        'temperature': '0', 'language': language}, {'file': (filename + '.wav', audio)})
    started = time.perf_counter()
    with urllib.request.urlopen(urllib.request.Request(base_url + '/v1/audio/transcriptions',
        data=body, headers={'Content-Type': content_type}), timeout=900) as response:
        result = json.load(response)
    if not isinstance(result.get('text'), str):
        raise ValueError('ASR returned no transcript text.')
    return result, time.perf_counter() - started


def judge(base_url, audio, item):
    result, elapsed = transcribe(base_url, audio, item['asr_language'], item['call_id'])
    text = result['text'].strip()
    return {'transcript': text, 'transcript_normalized': normalize_transcript(text),
        'detected_language': result.get('language'), 'asr_seconds': round(elapsed, 6),
        'exact': normalize_transcript(item['text']) == normalize_transcript(text),
        'similarity_percent': similarity(item['text'], text)}


def version_metadata(container):
    script = """import importlib.metadata as m,json,sys,hashlib,pathlib
import faster_qwen3_tts, qwen_tts
names=['faster-qwen3-tts','torch','transformers','huggingface-hub','triton','ssml-h-tools']
versions={n:m.version(n) for n in names}
files=[]
for module in (faster_qwen3_tts,qwen_tts):
 root=pathlib.Path(module.__file__).parent
 for path in sorted(root.rglob('*.py')):
  files.append((module.__name__+'/'+path.relative_to(root).as_posix(),hashlib.sha256(path.read_bytes()).hexdigest()))
print(json.dumps({'python':sys.version.split()[0],'packages':versions,'inference_source_sha256':hashlib.sha256(json.dumps(files).encode()).hexdigest()}))
"""
    return json.loads(docker('exec', container, 'python', '-c', script, timeout=90).stdout)
