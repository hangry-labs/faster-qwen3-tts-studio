# syntax=docker/dockerfile:1
# Default/local target: tiny. CI explicitly builds baked and tiny.
FROM python:3.13-slim@sha256:d98cc29d3266e535dd9da1099688d9cb3ca4753813571e071763d17725460962 AS dependencies

LABEL app.hangrylabs.project="faster-qwen3-tts-studio"

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/persistent/huggingface \
    TORCHINDUCTOR_CACHE_DIR=/app/persistent/torch_inductor \
    QWEN_STUDIO_DATA=/app/persistent/studio

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.runtime.txt ./
RUN python -m pip install --only-binary=:all: --require-hashes -r requirements.runtime.txt

FROM dependencies AS model-assets
COPY scripts/prefetch_models.py ./scripts/
COPY src/faster_qwen3_tts/standalone_ui/model_catalog.py ./src/faster_qwen3_tts/standalone_ui/
RUN python -u scripts/prefetch_models.py --cache-root /app/baked-models/huggingface

FROM dependencies AS app
COPY pyproject.toml README*.md VERSION LICENSE NOTICE THIRD_PARTY_NOTICES.md ./
COPY src/ ./src/
RUN python -m pip install --no-build-isolation --no-deps '.[studio]' \
    && python -m pip check
RUN python -c "from importlib.metadata import distributions; print('\n'.join(sorted({d.metadata['Name'] + '==' + d.version for d in distributions()})))" > /app/runtime-constraints.txt
COPY scripts/collect_runtime_licenses.py ./scripts/
COPY docs/LICENSING.md docs/UPSTREAMS.md ./docs/
RUN python scripts/collect_runtime_licenses.py --output /app/licenses/runtime
COPY examples/ ./examples/

ARG BUILD_DATE=unknown
ARG VCS_REF=unknown
ARG IMAGE_VERSION=dev
ARG SOURCE_IMAGE=local-build
ENV QWEN_STUDIO_BUILD_ID=${VCS_REF} \
    QWEN_STUDIO_BUILD_DATE=${BUILD_DATE} \
    QWEN_STUDIO_IMAGE_VERSION=${IMAGE_VERSION}
LABEL org.opencontainers.image.source="https://github.com/hangry-labs/faster-qwen3-tts-studio" \
    org.opencontainers.image.title="Hangry Labs Faster Qwen3-TTS Studio" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.revision="${VCS_REF}" \
    org.opencontainers.image.version="${IMAGE_VERSION}" \
    app.hangrylabs.sources="${SOURCE_IMAGE}"

EXPOSE 7860
CMD ["python", "-m", "faster_qwen3_tts.standalone_ui.docker_entrypoint"]

FROM model-assets AS baked
# Inherit the large model layer directly instead of keeping a second copy in
# a separate asset stage and COPY layer during hosted-runner publication.
COPY --from=app /app /app
RUN python -m pip install --no-build-isolation --no-deps '.[studio]' \
    && python -m pip check
ARG BUILD_DATE=unknown
ARG VCS_REF=unknown
ARG IMAGE_VERSION=dev
ARG SOURCE_IMAGE=local-build
ENV QWEN_STUDIO_BUILD_ID=${VCS_REF} \
    QWEN_STUDIO_BUILD_DATE=${BUILD_DATE} \
    QWEN_STUDIO_IMAGE_VERSION=${IMAGE_VERSION}
LABEL org.opencontainers.image.source="https://github.com/hangry-labs/faster-qwen3-tts-studio" \
    org.opencontainers.image.title="Hangry Labs Faster Qwen3-TTS Studio" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.revision="${VCS_REF}" \
    org.opencontainers.image.version="${IMAGE_VERSION}" \
    app.hangrylabs.sources="${SOURCE_IMAGE}"
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1
EXPOSE 7860
CMD ["python", "-m", "faster_qwen3_tts.standalone_ui.docker_entrypoint"]

FROM app AS source-assets
COPY scripts/collect_runtime_sources.py scripts/runtime_sources.toml ./scripts/
# Source indexes are enabled only in this build stage, never in product images.
RUN python -c "from pathlib import Path; import re; files=list(Path('/etc/apt/sources.list.d').glob('*.sources')); assert files, 'Expected Debian deb822 sources'; [p.write_text(re.sub(r'^Types: deb$', 'Types: deb deb-src', p.read_text(), flags=re.M)) for p in files]" \
    && apt-get update \
    && python scripts/collect_runtime_sources.py --output /sources
COPY --from=app /app/licenses/runtime /sources/notices
COPY Dockerfile requirements.runtime.txt requirements.runtime.in /sources/build/
COPY scripts/collect_runtime_licenses.py scripts/collect_runtime_sources.py scripts/runtime_sources.toml /sources/build/
COPY LICENSE NOTICE THIRD_PARTY_NOTICES.md docs/LICENSING.md /sources/

FROM scratch AS sources
COPY --from=source-assets /sources /sources
ARG VCS_REF=unknown
ARG IMAGE_VERSION=dev
LABEL org.opencontainers.image.source="https://github.com/hangry-labs/faster-qwen3-tts-studio" \
    org.opencontainers.image.title="Faster Qwen3-TTS Studio corresponding sources" \
    org.opencontainers.image.revision="${VCS_REF}" \
    org.opencontainers.image.version="${IMAGE_VERSION}"

FROM scratch AS evidence
COPY --from=app /app/licenses/runtime /runtime
COPY --from=app /app/runtime-constraints.txt /runtime-constraints.txt
COPY --from=model-assets /app/baked-models/huggingface/model-manifest.json /models/model-manifest.json
COPY --from=source-assets /sources/manifest.json /sources/manifest.json
COPY --from=source-assets /sources/SHA256SUMS /sources/SHA256SUMS

FROM app AS checks
COPY Dockerfile requirements.runtime.in ./
COPY tests/ ./tests/
COPY scripts/ ./scripts/
COPY docs/ ./docs/
COPY benchmarks/ ./benchmarks/
RUN python -m pip install --only-binary=:all: 'pytest>=8,<10'
RUN --network=none python -m pytest -q -p no:cacheprovider --ignore=tests/test_e2e_parity.py tests

FROM app AS tiny
ENV HF_HUB_OFFLINE=0 \
    TRANSFORMERS_OFFLINE=0
