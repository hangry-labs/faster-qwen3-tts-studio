# SPDX-License-Identifier: Apache-2.0
# Adapted from Hangry Labs VoxCPMTTS text_planning.py for Qwen codec budgets.
"""Bounded sentence/clause planning for spaced and CJK writing systems."""
from __future__ import annotations

import re

_UNIT = re.compile(r'[\u3400-\u9fff\u3040-\u30ff\u31f0-\u31ff\uac00-\ud7af]|'
                   r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
_SENTENCE = re.compile(r'[.!?。！？；;]["\'”’）)\]}」』》〉]*\s*')
_CLAUSE = re.compile(r'[,，、:：]\s*')


def split_text(text, *, max_chars=400, target_units=50, limit_units=80):
    """Prefer sentences, then clauses, then spaces; never exceed max_chars."""
    if not 1 <= target_units <= limit_units or max_chars < 1:
        raise ValueError('Text planning needs positive, ordered limits.')
    remaining = re.sub(r'\s+', ' ', text).strip()
    while remaining:
        units = list(_UNIT.finditer(remaining))
        if len(remaining) <= max_chars and len(units) <= limit_units:
            yield remaining
            return
        ceiling = min(max_chars, units[limit_units - 1].end() if len(units) > limit_units else len(remaining))
        target = min(ceiling, units[target_units - 1].end() if len(units) >= target_units else ceiling)
        prefix = remaining[:ceiling]
        sentences = [match.end() for match in _SENTENCE.finditer(prefix)]
        after_target = [end for end in sentences if end >= target]
        clauses = [match.end() for match in _CLAUSE.finditer(prefix) if match.end() >= target]
        spaces = [match.start() for match in re.finditer(r'\s+', prefix) if match.start() >= target]
        earlier_spaces = [match.start() for match in re.finditer(r'\s+', prefix)]
        boundary = (after_target[0] if after_target else clauses[0] if clauses else
                    sentences[-1] if sentences else spaces[0] if spaces else
                    earlier_spaces[-1] if earlier_spaces else ceiling)
        yield remaining[:boundary].strip()
        remaining = remaining[boundary:].strip()
