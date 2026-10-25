# Inherited NVIDIA research scripts

These scripts are retained for engine investigation, separate from product
performance qualification. Run them inside the Docker runtime with NVIDIA GPU
access and this directory mounted at `/benchmarks`. The installed model and
faster packages both come from this project.

Clone benchmarks require an authorized reference recording mounted in the
container. Set `QWEN_TTS_REF_AUDIO` to its container path and
`QWEN_TTS_REF_TEXT` to its exact transcript. There is no default recording,
transcript download or local ASR dependency. `custom_voice.py` uses a built-in
speaker instead. Mount a writable output directory if saving generated WAVs.

For example, after building the image and preparing permitted assets in a local
`benchmark-data` directory:

```bash
docker run --rm --gpus all \
  -v faster_qwen3_tts_studio_data:/app/persistent \
  -v ./benchmarks/research:/benchmarks:ro -v ./benchmark-data:/data -w /data \
  -e QWEN_TTS_REF_AUDIO=/data/reference.wav \
  -e QWEN_TTS_REF_TEXT="The exact words in your reference recording." \
  --entrypoint python faster-qwen3-tts-studio:dev /benchmarks/chunk_sweep.py
```

Generated WAVs go to the working directory, or `QWEN_TTS_BENCH_OUTPUT`. Preserve
measurement settings, hardware, warmup policy and the exact candidate identity
before comparing results. The [historical tables](../../docs/UPSTREAM_BENCHMARKS.md)
are upstream measurements, not results for this Docker build. Use the
[maintained product benchmark suite](../README.md) for product comparisons.
