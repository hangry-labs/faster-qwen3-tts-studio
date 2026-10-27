"""Source identity and integrity checks without network, Docker or GPU access."""
import copy
import hashlib
import io
import json
from unittest.mock import patch

import pytest

from scripts.collect_runtime_sources import (control_records, debian_sources, fetch, main,
                                             safe_path, verify, wheel_sources)


def test_debian_control_handles_empty_multiline_headers_and_crlf():
    records = control_records('Package: demo\r\nVersion: 1:2-3\r\nChecksums-Sha256:\r\n abc 3 a.tar.xz\r\n\r\n')
    assert records == [dict(Package='demo', Version='1:2-3', **{'Checksums-Sha256': '\nabc 3 a.tar.xz'})]


def test_debian_sources_require_exact_version_and_all_publisher_files():
    inventory = {'debian_packages': [dict(source_package='demo', source_version='1:2-3')] * 2}
    index = ('Package: demo\nVersion: 1:2-3\nDirectory: pool/main/d/demo\nChecksums-Sha256:\n'
             f" {'a'*64} 3 demo_2-3.dsc\n {'b'*64} 8 demo_2.orig.tar.xz\n\n"
             'Package: demo\nVersion: 3-1\nDirectory: pool/main/d/demo\nChecksums-Sha256:\n'
             f" {'c'*64} 9 demo_3-1.dsc\n")
    files, components = debian_sources(inventory, index)
    assert len(components) == 1
    assert components[0]['version'] == '1:2-3'
    assert [f['size'] for f in files] == [3, 8]
    inventory['debian_packages'][0]['source_version'] = '4-1'
    with pytest.raises(ValueError, match='Exact Debian source unavailable'):
        debian_sources(inventory, index)


@pytest.mark.parametrize('value', ['../escape', '/absolute', 'debian/../escape',
                                  r'debian\escape', 'debian//file', 'C:/escape'])
def test_source_paths_cannot_escape_bundle(value):
    with pytest.raises(ValueError, match='Unsafe'):
        safe_path(value)


def wheel_fixture():
    inventory = {'python_packages': [dict(name='demo', version='1.0', declared_license='LGPL-2.1-or-later',
        native_files=[dict(file='demo/lib.so.1', sha256='a'*64)])]}
    policy = {'wheels': {'demo': dict(version='1.0', native_pattern=r'lib\.so',
        native={'demo/lib.so.1': 'a'*64}, sources=['demo.tar.xz'])},
        'sources': {'demo.tar.xz': dict(size=3, sha256='b'*64, url='https://example.invalid/demo.tar.xz')}}
    return inventory, policy


def test_wheel_review_requires_matching_native_payload_and_version():
    inventory, policy = wheel_fixture()
    files, components = wheel_sources(inventory, policy)
    assert files[0]['file'] == 'wheels/demo.tar.xz'
    assert components[0]['native'] == {'demo/lib.so.1': 'a'*64}
    for change in ('version', 'sha256', 'extra'):
        bad = copy.deepcopy(inventory)
        if change == 'version':
            bad['python_packages'][0]['version'] = '2.0'
        elif change == 'sha256':
            bad['python_packages'][0]['native_files'][0]['sha256'] = 'c'*64
        else:
            bad['python_packages'][0]['native_files'].append(dict(file='demo/otherlib.so.2', sha256='d'*64))
        with pytest.raises(ValueError, match='source review|source review must'):
            wheel_sources(bad, policy)


def test_unknown_copyleft_dependency_requires_review():
    inventory, policy = wheel_fixture()
    inventory['python_packages'].append(dict(name='another', version='1', declared_license='MPL-2.0'))
    with pytest.raises(ValueError, match='Unreviewed copyleft'):
        wheel_sources(inventory, policy)


def test_bsd_wrapper_does_not_hide_bundled_gnu_runtime():
    inventory, policy = wheel_fixture()
    inventory['python_packages'].append(dict(name='another', version='1', declared_license='BSD-3-Clause',
        native_files=[dict(file='another.libs/libgomp-hidden.so.1', sha256='e'*64)]))
    with pytest.raises(ValueError, match='Unreviewed bundled native'):
        wheel_sources(inventory, policy)


def test_source_download_replaces_bad_cache_and_checks_redirect_and_hash(tmp_path):
    data = b'source archive'
    entry = dict(file='debian/demo/demo.tar.xz', size=len(data),
                 sha256=hashlib.sha256(data).hexdigest(), urls=['https://example.invalid/demo.tar.xz'])
    destination = tmp_path / entry['file']
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b'x' * len(data))
    def response(url, **kwargs):
        result = io.BytesIO(data)
        result.url = url
        return result
    with patch('scripts.collect_runtime_sources.urlopen', side_effect=response):
        fetch(entry, tmp_path)
    assert destination.read_bytes() == data
    with patch('scripts.collect_runtime_sources.urlopen') as network:
        fetch(entry, tmp_path)
        network.assert_not_called()
    destination.unlink()
    with patch('scripts.collect_runtime_sources.urlopen', side_effect=lambda _, **kw: response('http://example.invalid/source')), \
         patch('scripts.collect_runtime_sources.time.sleep'):
        with pytest.raises(RuntimeError, match='Could not obtain'):
            fetch(entry, tmp_path)
    assert not destination.exists()
    assert not destination.with_name(destination.name+'.part').exists()
    with patch('scripts.collect_runtime_sources.urlopen', side_effect=response), \
         patch('scripts.collect_runtime_sources.time.sleep'):
        with pytest.raises(RuntimeError):
            fetch({**entry, 'sha256': 'f'*64}, tmp_path)
    assert not destination.exists()


def test_verified_bundle_rejects_missing_or_changed_source(tmp_path):
    path = tmp_path / 'source.tar'
    path.write_bytes(b'source')
    manifest = dict(source_collection_complete=True, files=[dict(file=path.name, size=6,
                   sha256=hashlib.sha256(b'source').hexdigest())])
    (tmp_path/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    verify(tmp_path)
    path.write_bytes(b'alter!')
    with pytest.raises(ValueError, match='changed source'):
        verify(tmp_path)
    path.unlink()
    with pytest.raises(ValueError, match='Missing'):
        verify(tmp_path)


@pytest.mark.parametrize('plan_only', [False, True])
def test_failed_collection_invalidates_old_manifest_but_plan_never_writes(tmp_path, monkeypatch, plan_only):
    inventory, _ = wheel_fixture()
    inventory['debian_packages'] = []
    inventory['python_packages'][0]['review_required'] = False
    (tmp_path/'inventory.json').write_text(json.dumps(inventory), encoding='utf-8')
    (tmp_path/'policy.toml').write_text('[wheels.demo]\nversion="2.0"\nsources=[]\n', encoding='utf-8')
    (tmp_path/'apt-index').write_text('', encoding='utf-8')
    manifest = tmp_path/'manifest.json'
    manifest.write_text('{"source_collection_complete":true}', encoding='utf-8')
    argv = ['collect_runtime_sources.py', '--inventory', str(tmp_path/'inventory.json'),
            '--policy', str(tmp_path/'policy.toml'), '--apt-index', str(tmp_path/'apt-index'),
            '--output', str(tmp_path)] + (['--plan'] if plan_only else [])
    monkeypatch.setattr('sys.argv', argv)
    with pytest.raises(ValueError, match='review must be updated'):
        main()
    assert manifest.exists() is plan_only
