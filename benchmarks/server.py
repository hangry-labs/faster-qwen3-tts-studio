"""Benchmark-only native adapter over the same Studio planner, FIFO and encoders.

The production Studio continues to use Faster Qwen. No alternate backend is
installed or enabled there by this benchmark harness.
"""
from __future__ import annotations
from collections import OrderedDict
from dataclasses import replace
from pathlib import Path
import argparse
import hashlib
import time

from faster_qwen3_tts.standalone_ui.runtime import StudioEngine, MODELS


class NativeAdapter:
    def __init__(self, model):
        self.model = model
        self.prompts = OrderedDict()
        self.last_reference_cache_hit = None
        self.last_reference_preparation_ms = None

    @staticmethod
    def _bytes(prompts):
        return sum((item.ref_code.numel() * item.ref_code.element_size() if item.ref_code is not None else 0) +
            item.ref_spk_embedding.numel() * item.ref_spk_embedding.element_size() for item in prompts)

    def clear_voice_prompt_cache(self):
        self.prompts.clear()

    def _options(self, options):
        options = dict(options)
        # Match Faster's explicit sampling defaults rather than a checkpoint's
        # optional generation_config overrides. Identical seeds need not produce
        # identical recordings across two different sampling implementations.
        options.update(do_sample=True, top_p=1., subtalker_dosample=True,
            subtalker_top_p=1., subtalker_top_k=options.get('top_k', 50),
            subtalker_temperature=options.get('temperature', .9))
        return options

    def generate_custom_voice(self, **options):
        return self.model.generate_custom_voice(**self._options(options))

    def generate_voice_design(self, **options):
        return self.model.generate_voice_design(**self._options(options))

    def generate_voice_clone(self, **options):
        options = dict(options)
        if options.pop('instruct', ''):
            raise ValueError('Experimental Base direction is not part of the standard inference comparison.')
        reference = options.pop('ref_audio')
        text = options.pop('ref_text', '')
        identity_only = options.pop('xvec_only', False)
        key = (hashlib.sha256(Path(reference).read_bytes()).digest(), text if not identity_only else '', identity_only)
        started = time.perf_counter()
        self.last_reference_cache_hit = key in self.prompts
        if key not in self.prompts:
            prompts = self.model.create_voice_clone_prompt(ref_audio=reference, ref_text=text,
                x_vector_only_mode=identity_only)
            cached = [replace(item, ref_code=item.ref_code.cpu() if item.ref_code is not None else None,
                ref_spk_embedding=item.ref_spk_embedding.cpu()) for item in prompts]
            size = self._bytes(cached)
            if size <= 8 * 1024 * 1024:
                self.prompts[key] = cached
                while len(self.prompts) > 8 or sum(self._bytes(value) for value in self.prompts.values()) > 8 * 1024 * 1024:
                    self.prompts.popitem(last=False)
            else:
                cached = prompts
        else:
            cached = self.prompts.pop(key); self.prompts[key] = cached
        device = self.model.device
        prompts = [replace(item, ref_code=item.ref_code.to(device) if item.ref_code is not None else None,
            ref_spk_embedding=item.ref_spk_embedding.to(device)) for item in cached]
        self.last_reference_preparation_ms = (time.perf_counter() - started) * 1000
        return self.model.generate_voice_clone(voice_clone_prompt=prompts, **self._options(options))

    def __getattr__(self, name):
        if name.endswith('_streaming'):
            # Standard inference has no incremental waveform API. Emit one
            # complete chunk, honestly labelled buffered in benchmark metadata.
            method = getattr(self, name.removesuffix('_streaming'))
            def buffered(**options):
                options.pop('chunk_size', None)
                started = time.perf_counter()
                audio, rate = method(**options)
                yield audio, rate, {'decode_ms': (time.perf_counter() - started) * 1000}
            return buffered
        raise AttributeError(name)


class NativeEngine(StudioEngine):
    def _load(self, model_id):
        if self.model_id == model_id and self.model is not None:
            return
        import torch
        from huggingface_hub import snapshot_download
        from qwen_tts import Qwen3TTSModel
        self._state('loading'); self._unload()
        path = snapshot_download(model_id, revision=MODELS[model_id]['revision'], local_files_only=True)
        self.model = NativeAdapter(Qwen3TTSModel.from_pretrained(path, device_map='cuda:0',
            dtype=torch.bfloat16, attn_implementation='sdpa', local_files_only=True))
        self.models[model_id] = self.model
        self.model_id = model_id; self._state('ready')


def create_benchmark_app(engine_name, *, engine=None, data_dir=None):
    from faster_qwen3_tts import __version__
    from faster_qwen3_tts.standalone_ui.server import create_app
    app = create_app(engine or (NativeEngine() if engine_name == 'native' else StudioEngine()), data_dir)
    @app.post('/benchmark/memory/reset')
    def reset_memory():
        import torch
        if torch.cuda.is_initialized():
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
        return memory()

    @app.get('/benchmark/memory')
    def memory():
        import torch
        if not torch.cuda.is_initialized():
            return dict.fromkeys(['allocated_mib', 'reserved_mib', 'peak_allocated_mib', 'peak_reserved_mib'], 0.)
        return {key: round(value() / 1024**2, 2) for key, value in {
            'allocated_mib': torch.cuda.memory_allocated, 'reserved_mib': torch.cuda.memory_reserved,
            'peak_allocated_mib': torch.cuda.max_memory_allocated,
            'peak_reserved_mib': torch.cuda.max_memory_reserved}.items()}

    @app.get('/benchmark/info')
    def info():
        from benchmarks.common import harness_metadata
        return {'engine': engine_name, 'version': __version__, 'models': MODELS,
            'harness': harness_metadata(), 'inference_workers': 1,
            'dtype': 'bfloat16', 'attention': 'sdpa',
            'incremental_waveforms': engine_name == 'faster',
            'native_policy': 'local standard inference; CPU prompt cache; explicit matching sampling settings',
            'cache_policy': 'pinned offline weights; per-worker temporary compiler cache'}
    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=['native', 'faster'], required=True)
    args = parser.parse_args()
    import uvicorn
    uvicorn.run(create_benchmark_app(args.engine), host='0.0.0.0', port=7860, log_level='warning')


if __name__ == '__main__':
    main()
