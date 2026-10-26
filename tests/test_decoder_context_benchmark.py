"""A context report must preserve paired evidence and aggregate actual audio/wall time."""
import json

import pytest

from benchmarks.decoder_context import report


def write_worker(tmp_path, phase, *, checksum='same'):
    context = [25,100,100,25][phase]
    row = dict(model='Qwen/model', context=context, phase=phase, case='long-en', repeat=0,
        codec_sha256=checksum, duration_s=12,
        wall_s=4 if context==25 else 6, ttfa_ms=100,
        peak_allocated_mib=2000 if context==25 else 2200,
        peak_reserved_mib=3000 if context==25 else 3200)
    (tmp_path/f'Qwen3-TTS-test-{phase}.json').write_text(json.dumps(dict(rows=[row], gpu='Test GPU',
        torch='test', transformers='test')))


def test_report_requires_complete_pairs_and_keeps_speed_memory_separate(tmp_path):
    for phase in range(4):
        write_worker(tmp_path, phase)
    result = report(tmp_path)
    assert result['samples'] == 4 and result['paired_cases'] == 1
    assert result['identical_codec_tokens']
    assert [row['realtime'] for row in result['summaries']] == [3,2]
    assert [row['peak_allocated_mib'] for row in result['summaries']] == [2000,2200]
    assert 'Test GPU' in (tmp_path/'RESULTS.md').read_text()


def test_incomplete_context_experiment_is_not_reported_as_success(tmp_path):
    write_worker(tmp_path, 0)
    with pytest.raises(ValueError, match='Incomplete'):
        report(tmp_path)
    assert not (tmp_path/'RESULTS.md').exists()


def test_report_does_not_hide_seeded_token_mismatches(tmp_path):
    for phase in range(4):
        write_worker(tmp_path, phase, checksum='different' if phase==2 else 'same')
    assert not report(tmp_path)['identical_codec_tokens']
