# Local development image; model weights download on demand into the data volume.
# Exact image/dependency/source qualification is required before redistribution.
FROM python:3.13-slim

LABEL app.hangrylabs.project="faster-qwen3-tts-studio"

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/persistent/huggingface \
    TORCHINDUCTOR_CACHE_DIR=/app/persistent/torch_inductor \
    QWEN_STUDIO_DATA=/app/persistent/studio

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 sox libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.dev.txt ./
RUN python -m pip install --only-binary=:all: -r requirements.dev.txt

COPY pyproject.toml README.md LICENSE NOTICE THIRD_PARTY_NOTICES.md ./
COPY faster_qwen3_tts/ ./faster_qwen3_tts/
RUN python -m pip install --only-binary=:all: -c requirements.dev.txt '.[studio]' \
    && python -m pip check
COPY scripts/collect_runtime_licenses.py ./scripts/
COPY docs/LICENSING.md ./docs/

EXPOSE 7860
CMD ["python", "-m", "faster_qwen3_tts.standalone_ui.server"]
