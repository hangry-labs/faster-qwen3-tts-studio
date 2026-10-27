"""Publishing rules run without registries, credentials or model dependencies."""
from subprocess import CompletedProcess
import shutil
from unittest.mock import patch

import pytest

from scripts.ci_images import (REGISTRIES, add_source_plan, check_release_checkout, check_unpublished,
                              inspect_digest, plan_images, run, verify_publication)


def test_main_publishes_only_moving_tags():
    plan = plan_images('push', 'refs/heads/main')
    assert plan['baked_tags'] == [f'{repo}:latest' for repo in REGISTRIES]
    assert plan['tiny_tags'] == [f'{repo}:latest_tiny' for repo in REGISTRIES]
    assert plan['release_tag'] == ''


@pytest.mark.parametrize('version', ['v1.0', 'v1.2.3'])
def test_tag_push_never_moves_latest(version):
    plan = plan_images('push', f'refs/tags/{version}')
    assert plan['baked_tags'] == [f'{repo}:{version}' for repo in REGISTRIES]
    assert plan['tiny_tags'] == [f'{repo}:{version}_tiny' for repo in REGISTRIES]
    assert plan['image_version'] == version[1:]


def test_manual_release_can_explicitly_add_moving_tags():
    plan = plan_images('workflow_dispatch', 'refs/heads/main', 'v1.0', True)
    assert len(plan['baked_tags']) == len(plan['tiny_tags']) == 4
    stable = plan_images('workflow_dispatch', 'refs/heads/main', 'v1.0', False)
    assert not any(':latest' in ref for ref in stable['baked_tags'] + stable['tiny_tags'])


@pytest.mark.parametrize('event,ref,tag,latest', [
    ('pull_request', 'refs/pull/1/merge', '', True),
    ('push', 'refs/heads/feature', '', False),
    ('workflow_dispatch', 'refs/heads/main', '', False),
    *[('workflow_dispatch', 'refs/heads/main', value, True) for value in
      ['latest', 'v1.0-snapshot', 'v1.0_tiny', 'v1', 'v1.2.3.4', 'v1.0\nv2.0', '$(id)', 'v1.0;id']],
])
def test_unsupported_or_injected_publication_identity_fails(event, ref, tag, latest):
    with pytest.raises(ValueError):
        plan_images(event, ref, tag, latest)


@pytest.mark.skipif(shutil.which('git') is None, reason='Git identity is exercised by source CI; runtime omits Git')
def test_manual_release_must_build_the_actual_git_tag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert run('git', 'init', '--quiet').returncode == 0
    def commit(message):
        result = run('git', '-c', 'user.name=CI test', '-c', 'user.email=ci@example.invalid',
                     'commit', '--allow-empty', '--quiet', '-m', message)
        assert result.returncode == 0, result.stderr
    commit('release')
    assert run('git', 'tag', 'v1.0').returncode == 0
    plan = plan_images('workflow_dispatch', 'refs/heads/main', 'v1.0')
    check_release_checkout(plan)
    commit('next snapshot')
    with pytest.raises(ValueError, match='selected commit'):
        check_release_checkout(plan)


def test_existing_stable_tag_is_never_overwritten():
    plan = plan_images('push', 'refs/tags/v1.0')
    with patch('scripts.ci_images.run', return_value=CompletedProcess([], 0, 'manifest', '')):
        with pytest.raises(ValueError, match='already exists'):
            check_unpublished(plan)


def test_missing_registry_tag_is_allowed_but_auth_errors_are_not_absence():
    plan = plan_images('push', 'refs/tags/v1.0')
    with patch('scripts.ci_images.run', return_value=CompletedProcess([], 1, '', 'manifest unknown')) as command:
        check_unpublished(plan)
        assert command.call_count == 4
    with patch('scripts.ci_images.run', return_value=CompletedProcess([], 1, '', 'unauthorized: access denied')):
        with pytest.raises(RuntimeError, match='credentials'):
            check_unpublished(plan)


def test_moving_tags_do_not_need_release_absence_checks():
    with patch('scripts.ci_images.run') as command:
        check_unpublished(plan_images('push', 'refs/heads/main'))
        command.assert_not_called()


def test_manifest_parser_returns_top_level_index_and_not_child_digest():
    top, child = 'sha256:' + 'a' * 64, 'sha256:' + 'b' * 64
    text = f'Name: image\nDigest:    {top}\nManifests:\n  Digest: {child}\n'
    with patch('scripts.ci_images.run', return_value=CompletedProcess([], 0, text, '')):
        assert inspect_digest('image:tag') == top


def test_mirrors_and_all_tags_must_match_both_build_outputs():
    full, tiny = 'sha256:' + 'a' * 64, 'sha256:' + 'b' * 64
    plan = plan_images('workflow_dispatch', 'refs/heads/main', 'v1.0', True)
    with patch('scripts.ci_images.inspect_digest', side_effect=lambda ref: tiny if ref.endswith('_tiny') else full):
        records = verify_publication(plan, full, tiny)
    assert len(records) == 8
    with patch('scripts.ci_images.inspect_digest', return_value=tiny), patch('scripts.ci_images.time.sleep'):
        with pytest.raises(RuntimeError, match='differs'):
            verify_publication(plan, full, tiny)


def test_invalid_build_digest_cannot_be_verified():
    with pytest.raises(ValueError, match='valid OCI digest'):
        verify_publication(plan_images('push', 'refs/heads/main'), '', 'not a digest')


def test_sources_have_unique_build_identity_and_matching_stable_alias():
    plan = add_source_plan(plan_images('push', 'refs/tags/v1.0'), 'a'*40, '1234', '2')
    assert plan['source_image'] == f'{REGISTRIES[0]}:sources-' + 'a'*40 + '-1234-2'
    assert len(plan['source_tags']) == 4
    assert f'{REGISTRIES[0]}:v1.0_sources' in plan['source_tags']
    other = add_source_plan(plan_images('push', 'refs/heads/main'), 'a'*40, '1235', '1')
    assert other['source_image'] != plan['source_image']
    assert f'{REGISTRIES[0]}:latest_sources' in other['source_tags']
    with pytest.raises(ValueError, match='Source identity'):
        add_source_plan(plan, 'a'*40, '../bad', '1')


def test_source_only_partial_publication_cannot_be_overwritten():
    plan = add_source_plan(plan_images('push', 'refs/tags/v1.0'), 'a'*40, '1234', '1')
    def inspect(*command):
        return CompletedProcess([], 0, 'manifest', '') if command[-1].endswith('_sources') else CompletedProcess([], 1, '', 'manifest unknown')
    with patch('scripts.ci_images.run', side_effect=inspect):
        with pytest.raises(ValueError, match='already exists'):
            check_unpublished(plan)


def test_source_indexes_are_verified_in_both_registries():
    full, tiny, sources = ['sha256:'+char*64 for char in 'abc']
    plan = add_source_plan(plan_images('push', 'refs/tags/v1.0'), 'a'*40, '1234', '1')
    def digest(ref):
        return sources if ':sources-' in ref or ref.endswith('_sources') else tiny if ref.endswith('_tiny') else full
    with patch('scripts.ci_images.inspect_digest', side_effect=digest):
        assert len(verify_publication(plan, full, tiny, sources)) == 8
    with pytest.raises(ValueError, match='valid OCI digest'):
        verify_publication(plan, full, tiny)
