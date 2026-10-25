"""Prepare local snapshot/stable Git transitions. Publishing is a separate action."""
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

FILES = ('VERSION', 'pyproject.toml', 'src/faster_qwen3_tts/__init__.py', 'README.md', 'docs/dockerhub.md')
VALIDATION = [('task', 'validate'), ('task', 'package'), ('docker', 'build', '--check', '.'),
              ('docker', 'build', '--target', 'checks', '.'),
              ('docker', 'build', '--target', 'tiny', '-t', 'faster-qwen3-tts-studio:release-tiny', '.'),
              ('docker', 'build', '--target', 'baked', '-t', 'faster-qwen3-tts-studio:release-full', '.')]


def replace_once(pattern, replacement, text):
    result, count = re.subn(pattern, replacement, text, flags=re.M)
    if count != 1:
        raise ValueError('Expected exactly one version field: ' + pattern)
    return result


def package_version(display):
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?', display):
        raise ValueError('Versions must use X.Y or X.Y.Z.')
    return display + '.0' if display.count('.') == 1 else display


def prepare(original, next_version=''):
    snapshot = original['VERSION'].strip()
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?-snapshot', snapshot):
        raise ValueError('VERSION must identify a development snapshot.')
    stable = snapshot.removesuffix('-snapshot')
    expected_package = stable + '.dev0'
    if tomllib.loads(original['pyproject.toml'])['project']['version'] != expected_package:
        raise ValueError('Package version does not match VERSION.')
    match = re.search(r'^__version__ = "([^"]+)"$', original[FILES[2]], re.M)
    if not match or match[1] != snapshot:
        raise ValueError('Python runtime version does not match VERSION.')
    pieces = stable.split('.')
    next_snapshot = next_version or f'{pieces[0]}.{int(pieces[1]) + 1}-snapshot'
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?-snapshot', next_snapshot):
        raise ValueError('NEXT_VERSION must use X.Y-snapshot or X.Y.Z-snapshot.')
    next_display = next_snapshot.removesuffix('-snapshot')
    if tuple(map(int, package_version(next_display).split('.'))) <= tuple(map(int, package_version(stable).split('.'))):
        raise ValueError('The next snapshot must be newer than the release.')
    release = dict(original)
    release['VERSION'] = stable + '\n'
    release['pyproject.toml'] = replace_once(r'^version = "[^"]+"$', f'version = "{package_version(stable)}"', original['pyproject.toml'])
    release[FILES[2]] = replace_once(r'^__version__ = "[^"]+"$', f'__version__ = "{stable}"', original[FILES[2]])
    readme = original['README.md']
    heading = f'### v{snapshot}'
    heading_index = readme.find(heading + '\n')
    if heading_index < 0:
        raise ValueError('README Version History is missing the snapshot heading.')
    start = readme.rfind('<details>', 0, heading_index)
    end = readme.find('</details>', heading_index)
    if start < 0 or end < 0:
        raise ValueError('Snapshot history must live in a collapsible details section.')
    end += len('</details>')
    section = readme[start:end]
    bullets = section.find('\n- ', section.find(heading))
    if bullets < 0:
        raise ValueError('The snapshot needs release-note bullets before promotion.')
    promoted = (f'<details>\n<summary><strong>v{stable} release notes</strong></summary>\n\n### v{stable}\n\n'
        f'Source release `v{stable}`, Python package `{package_version(stable)}`. The source tag triggers '
        'container publication. Verify full/tiny registry indexes and add their digest-pinned '
        'deployment references before announcing availability.\n' + section[bullets:])
    release['README.md'] = readme[:start] + promoted + readme[end:]
    publication = re.compile(r'\*\*Publication status:\*\*.*?(?=\n\n)', re.S)
    release['docs/dockerhub.md'], count = publication.subn(
        f'**Publication status:** source release `v{stable}` prepares the versioned full/tiny tags. '
        'Availability requires a successful publishing workflow and verified registry digests.', original['docs/dockerhub.md'])
    if count != 1:
        raise ValueError('Docker Hub documentation needs exactly one publication-status paragraph.')
    following = dict(release)
    following['VERSION'] = next_snapshot + '\n'
    following['pyproject.toml'] = replace_once(r'^version = "[^"]+"$', f'version = "{next_display}.dev0"', release['pyproject.toml'])
    following[FILES[2]] = replace_once(r'^__version__ = "[^"]+"$', f'__version__ = "{next_snapshot}"', release[FILES[2]])
    new_section = (f'<details>\n<summary><strong>v{next_snapshot} development notes</strong></summary>\n\n'
        f'### v{next_snapshot}\n\nDevelopment version after `v{stable}`. Rolling `latest` and `latest_tiny` '
        'tags follow `main`; immutable release tags remain unchanged.\n\n- No changes recorded yet.\n\n</details>\n\n')
    following['README.md'] = release['README.md'][:start] + new_section + release['README.md'][start:]
    return {'tag': 'v' + stable, 'version': stable, 'package_version': package_version(stable),
            'next_snapshot': next_snapshot}, release, following


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def run(root, *, dry_run=False, next_version='', skip_validation=False, show_diff=False):
    original_bytes = {file: (root / file).read_bytes() for file in FILES}
    original = {file: (root / file).read_text(encoding='utf-8') for file in FILES}
    plan, release, following = prepare(original, next_version)
    branch = git(root, 'branch', '--show-current')
    if branch != 'main':
        raise ValueError('Release promotion must run from main.')
    if git(root, 'tag', '--list', plan['tag']):
        raise ValueError('The release tag already exists. Tags are immutable.')
    dirty = git(root, 'status', '--porcelain', '--untracked-files=all')
    if dirty and not dry_run:
        raise ValueError('The working tree must be clean before a real release.')
    print(json.dumps({**plan, 'dry_run': dry_run, 'working_tree_clean': not bool(dirty),
                      'changed_files': list(FILES), 'validation': [] if skip_validation else [' '.join(c) for c in VALIDATION]}, indent=2))
    if show_diff:
        for label, before, after in [('release', original, release), ('next snapshot', release, following)]:
            for file in FILES:
                print(''.join(difflib.unified_diff(before[file].splitlines(True), after[file].splitlines(True),
                    fromfile=file, tofile=label + '/' + file)), end='')
    if dry_run:
        print('Both transformations validated in memory. No files, builds, commits, tags or remote refs changed.')
        return
    subprocess.run(['git', 'fetch', 'origin', 'main', '--tags'], cwd=root, check=True)
    if git(root, 'rev-parse', 'HEAD') != git(root, 'rev-parse', 'refs/remotes/origin/main'):
        raise ValueError('main must match origin/main before release.')
    if git(root, 'tag', '--list', plan['tag']):
        raise ValueError('The release tag exists on the fetched history.')
    committed = False
    try:
        for file in FILES:
            (root / file).write_text(release[file], encoding='utf-8', newline='\n')
        if not skip_validation:
            for command in VALIDATION:
                subprocess.run(command, cwd=root, check=True)
        subprocess.run(['git', 'add', '--', *FILES], cwd=root, check=True)
        subprocess.run(['git', 'commit', '-m', 'release: ' + plan['tag']], cwd=root, check=True)
        committed = True
        subprocess.run(['git', 'tag', '-a', plan['tag'], '-m', 'Release ' + plan['tag']], cwd=root, check=True)
        for file in FILES:
            (root / file).write_text(following[file], encoding='utf-8', newline='\n')
        subprocess.run(['git', 'add', '--', *FILES], cwd=root, check=True)
        subprocess.run(['git', 'commit', '-m', 'chore: start ' + plan['next_snapshot']], cwd=root, check=True)
    except BaseException:
        if not committed:
            for file in FILES:
                (root / file).write_bytes(original_bytes[file])
            subprocess.run(['git', 'reset', '--', *FILES], cwd=root, check=True)
        else:
            print('Promotion stopped after the release commit. Inspect local refs before continuing; no refs were pushed.', file=sys.stderr)
        raise
    print('Local release and next snapshot prepared. No publication occurred. Publish only when authorized:')
    print('  git push --atomic origin main ' + plan['tag'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--next-version', default='')
    parser.add_argument('--skip-validation', action='store_true')
    parser.add_argument('--show-diff', action='store_true')
    args = parser.parse_args()
    run(Path(__file__).resolve().parents[1], dry_run=args.dry_run, next_version=args.next_version,
        skip_validation=args.skip_validation, show_diff=args.show_diff)
