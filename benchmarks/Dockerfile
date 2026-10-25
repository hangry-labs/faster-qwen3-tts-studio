ARG BASE_IMAGE=faster-qwen3-tts-studio:dev
FROM ${BASE_IMAGE}
COPY benchmarks/ /app/benchmarks/
COPY NOTICE THIRD_PARTY_NOTICES.md /app/
LABEL app.hangrylabs.benchmark="faster-qwen3-tts-studio"
ENTRYPOINT ["python", "-m", "benchmarks.server"]
CMD ["--engine", "faster"]
