"""Long-input protection preserves speech and prefers natural boundaries."""
import re

import pytest

from faster_qwen3_tts.standalone_ui.text_planning import split_text


def test_sentence_boundary_wins_over_later_whitespace():
    first = 'This is a complete sentence. '
    text = first + 'another word ' * 50
    sections = list(split_text(text, max_chars=80))
    assert sections[0] == first.strip()
    assert all(0 < len(part) <= 80 for part in sections)
    assert ' '.join(sections) == re.sub(r'\s+', ' ', text).strip()


def test_cjk_has_word_budget_without_whitespace_and_preserves_punctuation():
    text = '这是第一句话。' * 30
    sections = list(split_text(text, target_units=10, limit_units=20))
    assert len(sections) > 1
    assert all(part.endswith('。') for part in sections)
    assert ''.join(sections) == text


def test_clauses_precede_whitespace_when_the_sentence_is_long():
    text = 'one two three four, five six seven eight nine ten eleven twelve'
    parts = list(split_text(text, target_units=3, limit_units=7))
    assert parts[0] == 'one two three four,'
    assert ' '.join(parts) == text


@pytest.mark.parametrize('text', ['x' * 2000, '。' * 1200, ' hello  world\n' * 100])
def test_hard_character_limit_and_no_lost_content(text):
    parts = list(split_text(text))
    assert all(0 < len(part) <= 400 for part in parts)
    assert re.sub(r'\s+', '', ''.join(parts)) == re.sub(r'\s+', '', text)


def test_short_text_is_kept_in_one_call():
    assert list(split_text('Hello, world.')) == ['Hello, world.']
