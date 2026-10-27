# SPDX-License-Identifier: MIT AND Apache-2.0
# Portions adapted from Qwen3-TTS, Copyright 2026 The Alibaba Qwen team.
# Preserve NOTICE and the Apache-2.0 text in THIRD_PARTY_NOTICES.md.
"""Bounded incremental text and conditioning for one voice-cloning generation."""
from __future__ import annotations

from collections import deque
import threading
import time


LIVE_MODEL = 'Qwen/Qwen3-TTS-12Hz-1.7B-Base'


def validate_live_model(model):
    if model != LIVE_MODEL:
        raise ValueError('Live text-input streaming supports only ' + LIVE_MODEL +
                         '. Use the complete-text APIs for 0.6B models.')


class TextInput:
    """Accept text before/after tokenizer attachment; never revise consumed tokens."""

    def __init__(self, cancelled=None, *, idle_timeout=15., max_seconds=120.,
                 max_chars=4000, max_tokens=1500):
        self.cancelled = cancelled if cancelled is not None else threading.Event()
        self.condition = threading.Condition()
        self.idle_timeout, self.max_seconds = idle_timeout, max_seconds
        self.max_chars, self.max_tokens = max_chars, max_tokens
        self.text, self.tokens = '', []
        self.finished = False
        self.tokenizer = None
        self.active_since = None
        self.last_input = time.monotonic()
        self.wait_seconds, self.wait_count = 0., 0

    def _check(self):
        if self.cancelled.is_set():
            raise InterruptedError('Live speech cancelled.')
        if self.active_since is not None:
            now = time.monotonic()
            if now-self.active_since >= self.max_seconds:
                raise TimeoutError('Live utterance exceeded its wall time limit.')
            if not self.finished and now-max(self.last_input, self.active_since) >= self.idle_timeout:
                raise TimeoutError('No new text before the live input timeout. Send text or finish the input.')

    def _tokenize(self):
        if self.tokenizer is None:
            return
        pieces = self.tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str(self.text)
        end = len(self.text) if self.finished else (pieces[-2][1][0] if len(pieces) > 2 else 0)
        encoding = self.tokenizer.backend_tokenizer.encode(self.text, add_special_tokens=False)
        if len(encoding.ids) > self.max_tokens:
            raise ValueError('Live text exceeds the input token limit.')
        if encoding.ids[:len(self.tokens)] != self.tokens:
            raise ValueError('Text changed an already committed token boundary.')
        count = 0
        for _, token_end in encoding.offsets:
            if token_end > end:
                break
            count += 1
        # Completing a contraction can reduce the pretoken count. Retain the
        # already stable prefix rather than mistaking this for a token rewrite.
        self.tokens = encoding.ids[:max(count, len(self.tokens))]

    def append(self, text):
        with self.condition:
            self._check()
            if self.finished:
                raise ValueError('Text input is already finished.')
            if not isinstance(text, str):
                raise ValueError('A text fragment must be a string.')
            if len(self.text)+len(text) > self.max_chars:
                raise ValueError('Live text exceeds the input character limit.')
            if text:
                self.text += text
                self.last_input = time.monotonic()
                self._tokenize()
                self.condition.notify_all()

    def finish(self):
        with self.condition:
            self._check()
            if self.finished:
                raise ValueError('Text input is already finished.')
            if not self.text.strip():
                raise ValueError('Send some text before finishing the input.')
            self.finished = True
            self._tokenize()
            self.condition.notify_all()

    def cancel(self):
        with self.condition:
            self.cancelled.set()
            self.condition.notify_all()

    def attach(self, tokenizer):
        with self.condition:
            self.tokenizer = tokenizer
            self.active_since = time.monotonic()
            self._tokenize()
            self._check()
            self.condition.notify_all()

    def check(self):
        with self.condition:
            self._check()

    def _wait(self, predicate):
        started = time.monotonic()
        waited = False
        while not predicate():
            self._check()
            waited = True
            # Also observes cancellation set by a caller without cancel().
            self.condition.wait(.1)
        self._check()
        if waited:
            self.wait_count += 1
            self.wait_seconds += time.monotonic()-started

    def initial(self, minimum):
        with self.condition:
            self._wait(lambda: self.finished or (bool(self.text.strip()) and len(self.tokens) >= minimum))
            if not self.tokens:
                raise ValueError('The input did not contain any speech tokens.')
            count = len(self.tokens) if self.finished else minimum
            return self.tokens[:count], self.finished

    def next_token(self, offset):
        with self.condition:
            self._wait(lambda: self.finished or len(self.tokens) > offset)
            return self.tokens[offset] if offset < len(self.tokens) else None

    def metrics(self):
        with self.condition:
            return {'input_chars': len(self.text), 'input_tokens': len(self.tokens),
                    'input_finished': self.finished, 'input_wait_ms': round(self.wait_seconds*1000, 2),
                    'input_wait_count': self.wait_count}


class LiveConditioning:
    """Reference prefill followed by stable, demand-fed text embeddings."""

    def __init__(self, model, feed, initial_ids, finished):
        self.model, self.feed = model, feed
        self.initial_ids, self.initial_finished = list(initial_ids), finished
        self.assigned = len(initial_ids)
        self.pending = deque()
        self.eos_consumed = False
        self.pad = self.eos = None

    def build_icl(self, *, ref_id, ref_code, tts_pad_embed, tts_eos_embed):
        import torch
        talker = self.model.talker
        ids = torch.tensor([self.initial_ids], device=ref_id.device, dtype=ref_id.dtype)
        text = talker.text_projection(talker.get_text_embeddings()(torch.cat([ref_id, ids], dim=-1)))
        self.pad, self.eos = tts_pad_embed, tts_eos_embed
        if self.initial_finished:
            text = torch.cat([text, self.eos], dim=1)
        codebooks = [talker.get_input_embeddings()(ref_code[:, :1])]
        for index in range(1, talker.config.num_code_groups):
            codebooks.append(talker.code_predictor.get_input_embeddings()[index-1](ref_code[:, index:index+1]))
        codec = torch.cat(codebooks, dim=1).sum(1).unsqueeze(0)
        bos = talker.get_input_embeddings()(torch.tensor([[self.model.config.talker_config.codec_bos_id]],
                                                       device=ref_id.device, dtype=ref_id.dtype))
        codec = torch.cat([bos, codec], dim=1)
        positions, known = codec.shape[1], text.shape[1]
        prefix = text[:, :positions]
        if known < positions:
            prefix = torch.cat([prefix, self.pad.expand(-1, positions-known, -1)], dim=1)
        eos_position = ref_id.shape[1]+len(self.initial_ids)
        if self.initial_finished and eos_position < positions:
            self.eos_consumed = True
        for index in range(positions, known):
            self.pending.append((text[:, index:index+1], self.initial_finished and index == eos_position))
        return prefix+codec, self.pad

    def setup_speaker_only(self, trailing, pad):
        self.pad, self.eos = pad, trailing[:, -1:]
        for index in range(len(self.initial_ids)-1):
            self.pending.append((trailing[:, index:index+1], False))
        if self.initial_finished:
            self.pending.append((self.eos, True))

    def next_embedding(self, generation_step):
        import torch
        self.feed.check()
        if self.pending:
            embedding, is_eos = self.pending.popleft()
            self.eos_consumed = self.eos_consumed or is_eos
            return embedding
        if self.eos_consumed:
            return self.pad
        token = self.feed.next_token(self.assigned)
        if token is None:
            self.eos_consumed = True
            return self.eos
        self.assigned += 1
        ids = torch.tensor([[token]], device=self.pad.device, dtype=torch.long)
        embedding = self.model.talker.get_text_embeddings()(ids)
        # The MLP acts independently on each row. Only row zero enters speech.
        # Fixed shape prevents arrival-dependent BF16 rounding for tiny deltas.
        block = embedding.expand(-1, 4, -1).contiguous()
        return self.model.talker.text_projection(block)[:, :1]


def generate_voice_clone_live(wrapper, feed, request, reference, emit):
    """Run under the caller's exclusive inference lease and inference_mode."""
    import torch
    from .streaming import fast_generate_streaming
    base, model = wrapper.model, wrapper.model.model
    template = base._tokenize_texts([base._build_assistant_text('Live speech')])
    prompt, ref_ids, icl = wrapper._resolve_voice_clone_prompt(
        input_ids=template, ref_audio=reference, ref_text=request.ref_text,
        xvec_only=request.xvec_only, append_silence=True, voice_clone_prompt=None)
    minimum = max(1, prompt['ref_code'][0].shape[0]+1-ref_ids[0][:, 3:-2].shape[1]) if icl else 1
    feed.attach(base.processor.tokenizer)
    emit({'type': 'ready', 'model': request.model, 'xvec_only': request.xvec_only,
          'initial_text_tokens': minimum, 'reference_cache_hit': wrapper.last_reference_cache_hit})
    initial_ids, finished = feed.initial(minimum)
    live = LiveConditioning(model, feed, initial_ids, finished)
    prepared = wrapper._prepare_generation(text='', language=request.language,
        ref_text=request.ref_text, voice_clone_prompt=prompt, instruct=request.instruct,
        non_streaming_mode=False, live_text=live)
    m, talker, config, tie, tam, tth, pad, ref_codes = prepared
    codec = fast_generate_streaming(talker=talker, talker_input_embeds=tie, attention_mask=tam,
        trailing_text_hiddens=tth, tts_pad_embed=pad, config=config,
        predictor_graph=wrapper.predictor_graph, talker_graph=wrapper.talker_graph,
        max_new_tokens=request.max_new_tokens, temperature=request.temperature, top_k=request.top_k,
        repetition_penalty=request.repetition_penalty, chunk_size=request.chunk_size, text_source=live)
    try:
        yield from wrapper._decode_voice_clone_stream(m, ref_codes, codec,
            chunk_size=request.chunk_size, context_frames=request.decoder_context_frames)
    finally:
        codec.close()
