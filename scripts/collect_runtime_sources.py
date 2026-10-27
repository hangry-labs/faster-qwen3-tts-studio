"""Collect exact Debian sources and reviewed wheel bundles for a source image.

Run in the source-assets build stage after enabling deb-src indexes. Downloading
sources never builds or executes them. Collection is not automatic legal approval.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import time
import tomllib
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen


def sha256(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe_path(value: str) -> str:
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or '\\' in value or ':' in value or
            any(ord(char) < 32 for char in value) or
            any(part in ('', '.', '..') for part in value.split('/'))):
        raise ValueError('Unsafe source path: ' + value)
    return path.as_posix()


def control_records(text: str) -> list[dict]:
    records = []
    for paragraph in text.replace('\r\n', '\n').strip().split('\n\n'):
        record = {}
        key = None
        for line in paragraph.splitlines():
            if line.startswith((' ', '\t')) and key:
                record[key] += '\n' + line.strip()
            elif ':' in line:
                key, value = line.split(':', 1)
                record[key] = value.strip()
        if record:
            records.append(record)
    return records


def debian_sources(inventory: dict, index: str) -> tuple[list[dict], list[dict]]:
    available = {}
    for record in control_records(index):
        if 'Package' in record and 'Version' in record:
            key = record['Package'], record['Version']
            if key in available and available[key].get('Checksums-Sha256') != record.get('Checksums-Sha256'):
                raise ValueError('Conflicting Debian source checksums: ' + str(key))
            available[key] = record
    files, components = {}, []
    wanted = sorted({(p['source_package'], p['source_version']) for p in inventory['debian_packages']})
    for name, version in wanted:
        record = available.get((name, version))
        if record is None:
            raise ValueError(f'Exact Debian source unavailable: {name}={version}')
        directory = safe_path(record['Directory'])
        members = []
        for line in record.get('Checksums-Sha256', '').strip().splitlines():
            digest, size, filename = line.split()
            if '/' in safe_path(filename) or not re.fullmatch(r'[a-f0-9]{64}', digest):
                raise ValueError('Invalid Debian source member: ' + filename)
            path = safe_path(f'debian/{name}/{filename}')
            bases = ('https://deb.debian.org/debian/', 'https://deb.debian.org/debian-security/')
            if directory.startswith('pool/updates/'):
                bases = bases[::-1]
            entry = dict(file=path, size=int(size), sha256=digest,
                         urls=[base + directory + '/' + filename for base in bases])
            if path in files and files[path] != entry:
                raise ValueError('Conflicting source path: ' + path)
            files[path] = entry
            members.append(path)
        if not members or not any(name.endswith('.dsc') for name in members):
            raise ValueError('Debian sources lack checksums or descriptor: ' + name)
        components.append(dict(ecosystem='debian', name=name, version=version, files=members))
    return list(files.values()), components


def wheel_sources(inventory: dict, policy: dict) -> tuple[list[dict], list[dict]]:
    installed = {re.sub(r'[-_.]+', '-', p['name']).lower(): p for p in inventory['python_packages']}
    components, needed = [], set()
    for name, rule in policy['wheels'].items():
        package = installed.get(name)
        if package is None or package['version'] != rule['version']:
            raise ValueError('Wheel source review must be updated for ' + name)
        expected = rule.get('native', {})
        actual = {p['file']: p['sha256'] for p in package.get('native_files', [])
                  if re.search(rule.get('native_pattern', r'(?!)'), p['file'])}
        if actual != expected:
            raise ValueError('Wheel bundled binaries differ from source review: ' + name)
        needed.update(rule['sources'])
        components.append(dict(ecosystem='python', name=name, version=package['version'],
                               sources=rule['sources'], native=actual))
    for name, package in installed.items():
        license_text = package.get('declared_license', '') + '\n' + '\n'.join(package.get('license_classifiers', []))
        if re.search(r'\b(?:(?:[AL]?GPL|MPL)[-\d]|GNU (?:Lesser |Affero )?General Public License)', license_text) and name not in policy['wheels']:
            raise ValueError('Unreviewed copyleft Python package: ' + name)
        reviewed = policy['wheels'].get(name, {}).get('native', {})
        for entry in package.get('native_files', []):
            if re.search(r'(?:^|/)(?:libgomp|libgfortran|libquadmath|libsndfile|libsoxr)[-.]', entry['file']) and entry['file'] not in reviewed:
                raise ValueError('Unreviewed bundled native library: ' + name + '/' + entry['file'])
    files = []
    for name in sorted(needed):
        archive = policy['sources'][name]
        if not re.fullmatch(r'[a-f0-9]{64}', archive['sha256']):
            raise ValueError('Source archive requires a SHA256: ' + name)
        files.append(dict(file=safe_path('wheels/' + name), size=archive['size'],
                          sha256=archive['sha256'], urls=[archive['url']]))
    return files, components


def fetch(entry: dict, output: Path) -> dict:
    destination = output / safe_path(entry['file'])
    if destination.exists() and destination.stat().st_size == entry['size'] and sha256(destination) == entry['sha256']:
        return entry
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.part')
    error = None
    for attempt in range(3):
        for url in entry['urls']:
            if urlparse(url).scheme != 'https':
                raise ValueError('Sources must use verified HTTPS: ' + url)
            try:
                with urlopen(url, timeout=90) as response, temporary.open('wb') as stream:
                    if urlparse(response.url).scheme != 'https':
                        raise ValueError('Insecure source redirect: ' + response.url)
                    size = 0
                    while block := response.read(1024 * 1024):
                        size += len(block)
                        if size > entry['size']:
                            raise ValueError('Source size exceeds manifest: ' + entry['file'])
                        stream.write(block)
                if size != entry['size'] or sha256(temporary) != entry['sha256']:
                    raise ValueError('Source integrity check failed: ' + entry['file'])
                temporary.replace(destination)
                return entry
            except (OSError, HTTPError, URLError, ValueError) as exc:
                error = exc
                temporary.unlink(missing_ok=True)
        if attempt < 2:
            time.sleep(2 ** attempt)
    raise RuntimeError('Could not obtain ' + entry['file']) from error


def verify(output: Path) -> dict:
    manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('source_collection_complete') is not True:
        raise ValueError('Source collection is incomplete')
    for entry in manifest['files']:
        path = output / safe_path(entry['file'])
        if not path.is_file() or path.stat().st_size != entry['size'] or sha256(path) != entry['sha256']:
            raise ValueError('Missing or changed source: ' + entry['file'])
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=Path('/app/licenses/runtime/inventory.json'))
    parser.add_argument('--policy', type=Path, default=Path(__file__).with_name('runtime_sources.toml'))
    parser.add_argument('--apt-index', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        manifest = verify(args.output)
        print(f"Verified {len(manifest['files'])} source files.")
        return
    if not args.plan:
        args.output.mkdir(parents=True, exist_ok=True)
        # Even an early identity failure must invalidate the old completion flag.
        (args.output / 'manifest.json').unlink(missing_ok=True)
    raw_inventory = args.inventory.read_bytes()
    inventory = json.loads(raw_inventory)
    if any(p['review_required'] for group in ('python_packages', 'debian_packages') for p in inventory[group]):
        raise ValueError('Resolve missing runtime notices before collecting sources')
    policy = tomllib.loads(args.policy.read_text(encoding='utf-8'))
    if args.apt_index:
        index = args.apt_index.read_text(encoding='utf-8')
    else:
        names = sorted({p['source_package'] for p in inventory['debian_packages']})
        index = subprocess.check_output(['apt-cache', 'showsrc', '--only-source', *names], text=True)
    debian, debian_components = debian_sources(inventory, index)
    wheels, wheel_components = wheel_sources(inventory, policy)
    files = debian + wheels
    print(json.dumps(dict(debian_sources=len(debian_components), wheel_packages=len(wheel_components),
                          files=len(files), size_bytes=sum(f['size'] for f in files))), flush=True)
    if args.plan:
        return
    with ThreadPoolExecutor(max_workers=4) as workers:
        list(workers.map(lambda entry: fetch(entry, args.output), files))
    manifest = dict(schema_version=1, inventory_sha256=hashlib.sha256(raw_inventory).hexdigest(),
                    source_collection_complete=True, legal_approval=False,
                    components=debian_components + wheel_components, files=files)
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (args.output / 'SHA256SUMS').write_text(''.join(f"{e['sha256']}  {e['file']}\n" for e in files), encoding='utf-8')
    verify(args.output)
    print('Source collection and integrity verification complete; no automatic legal approval.')


if __name__ == '__main__':
    main()
