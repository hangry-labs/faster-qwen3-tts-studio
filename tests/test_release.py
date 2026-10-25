"""Release transitions transform real documents without publishing or rewriting refs."""
from pathlib import Path
import re
import subprocess
import shutil
from unittest.mock import patch

import pytest

from scripts.release import FILES, package_version, prepare, run

ROOT = Path(__file__).resolve().parents[1]


def documents():
    # Keep transition fixtures independent of the checkout's current release state.
    return {'VERSION': '1.0-snapshot\n', 'pyproject.toml': '[project]\nversion = "1.0.dev0"\n',
        FILES[2]: '__version__ = "1.0-snapshot"\n',
        'README.md': '# Studio\n\n## Version History\n\n<details>\n<summary><strong>v1.0-snapshot development notes</strong></summary>\n\n'
            '### v1.0-snapshot\n\nDevelopment notes.\n\n- Preserve this improvement.\n- Preserve this fix.\n\n</details>\n',
        'docs/dockerhub.md': '# Studio\n\n**Publication status:** Not published.\n\n## Images\n'}


def test_current_checkout_version_metadata_and_real_history():
    actual = {name: (ROOT / name).read_text(encoding='utf-8') for name in FILES}
    if actual['VERSION'].strip().endswith('-snapshot'):
        prepare(actual)
    else:
        import tomllib
        assert tomllib.loads(actual['pyproject.toml'])['project']['version'] == package_version(actual['VERSION'].strip())
        assert f'### v{actual["VERSION"].strip()}\n' in actual['README.md']


def test_actual_snapshot_promotes_and_preserves_every_note():
    old = documents()
    plan, stable, following = prepare(old)
    assert plan['tag'] == 'v1.0' and plan['package_version'] == '1.0.0'
    assert stable['VERSION'] == '1.0\n' and following['VERSION'] == '1.1-snapshot\n'
    for line in old['README.md'].splitlines():
        if line.startswith('- '):
            assert line in stable['README.md'] and line in following['README.md']
    assert '### v1.0\n' in stable['README.md']
    assert '### v1.1-snapshot\n' in following['README.md']
    assert '__version__ = "1.1-snapshot"' in following[FILES[2]]
    assert 'Verify full/tiny registry indexes' in stable['README.md']
    assert following['README.md'].count('<details>') == following['README.md'].count('</details>')
    assert old == documents()


def test_intro_version_and_shared_history_stay_in_sync_for_translated_readme_links():
    original = documents()
    original['README.md'] = 'Development version **v1.0-snapshot**. See the [version history](#version-history).\n\n' + original['README.md']
    _, release, following = prepare(original)
    assert release['README.md'].startswith('Source release **v1.0**.')
    assert following['README.md'].startswith('Development version **v1.1-snapshot**.')
    assert following['README.md'].index('### v1.1-snapshot') < following['README.md'].index('### v1.0\n')
    assert re.search(r'</details>\s*<details>\s*<summary><strong>v1.0 release notes', following['README.md'])


@pytest.mark.parametrize('next_version', ['1.0-snapshot', '0.9-snapshot', 'latest', '1.1', '$(id)', '1.2.3.4-snapshot'])
def test_invalid_or_older_next_versions_rejected(next_version):
    with pytest.raises(ValueError):
        prepare(documents(), next_version)


def test_patch_version_and_explicit_next_snapshot():
    original = documents()
    for name in FILES:
        original[name] = original[name].replace('1.0-snapshot', '1.0.2-snapshot').replace('1.0.dev0', '1.0.2.dev0')
    plan, stable, following = prepare(original, '1.0.3-snapshot')
    assert plan['tag'] == 'v1.0.2' and plan['package_version'] == '1.0.2'
    assert following['VERSION'] == '1.0.3-snapshot\n'


def test_version_drift_and_missing_release_history_fail():
    original = documents(); original['VERSION'] = '2.0-snapshot\n'
    with pytest.raises(ValueError, match='Package version'):
        prepare(original)
    original = documents(); original['README.md'] = '# No history\n'
    with pytest.raises(ValueError, match='snapshot heading'):
        prepare(original)


def test_dry_run_uses_real_transformations_without_commands_or_writes(tmp_path, capsys):
    for name, content in documents().items():
        target = tmp_path / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content, encoding='utf-8')
    before = {name: (tmp_path / name).read_bytes() for name in FILES}
    with patch('scripts.release.git', side_effect=['main', '', ' M README.md']), patch('scripts.release.subprocess.run') as command:
        run(tmp_path, dry_run=True, show_diff=True)
    assert not command.called and before == {name: (tmp_path / name).read_bytes() for name in FILES}
    output = capsys.readouterr().out
    assert '1.1-snapshot' in output and '### v1.0' in output and 'Both transformations validated' in output


def test_real_release_refuses_dirty_tree_before_mutation(tmp_path):
    for name, content in documents().items():
        target = tmp_path / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content, encoding='utf-8')
    with patch('scripts.release.git', side_effect=['main', '', ' M README.md']), patch('scripts.release.subprocess.run') as command:
        with pytest.raises(ValueError, match='clean'):
            run(tmp_path)
    assert not command.called


@pytest.mark.skipif(shutil.which('git') is None, reason='Host Git qualification; runtime image intentionally omits Git')
def test_local_release_creates_annotated_tag_and_next_snapshot_without_pushing(tmp_path):
    root = tmp_path / 'checkout'; root.mkdir()
    for name, content in documents().items():
        target = root / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content, encoding='utf-8')
    def git(*args, cwd=root):
        return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()
    git('init', '--quiet', '--initial-branch=main')
    git('config', 'user.name', 'Release test'); git('config', 'user.email', 'release@example.invalid')
    git('add', '.'); git('commit', '--quiet', '-m', 'Initial snapshot')
    initial = git('rev-parse', 'HEAD')
    remote = tmp_path / 'remote.git'
    git('clone', '--bare', '--quiet', str(root), str(remote), cwd=tmp_path)
    git('remote', 'add', 'origin', str(remote))
    run(root, skip_validation=True)
    assert git('cat-file', '-t', 'refs/tags/v1.0') == 'tag'
    assert git('show', 'v1.0:VERSION') == '1.0'
    assert git('show', 'HEAD:VERSION') == '1.1-snapshot'
    assert git('rev-parse', 'refs/remotes/origin/main') == initial
    assert git('rev-parse', 'HEAD', cwd=remote) == initial
    assert git('status', '--porcelain') == ''
