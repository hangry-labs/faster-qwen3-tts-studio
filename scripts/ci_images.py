"""Plan container tags and verify release identity and registry publication."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import time

REGISTRIES = ('hangrylabs/faster-qwen3-tts-studio',
              'ghcr.io/hangry-labs/faster-qwen3-tts-studio')
STABLE_TAG = re.compile(r'v\d+\.\d+(?:\.\d+)?\Z')
DIGEST = re.compile(r'sha256:[a-f0-9]{64}\Z')


def plan_images(event: str, ref: str, image_tag: str = '', push_latest: bool = False) -> dict:
    release = ''
    moving = False
    if event == 'push':
        if ref == 'refs/heads/main':
            moving = True
        elif ref.startswith('refs/tags/'):
            release = ref.removeprefix('refs/tags/')
        else:
            raise ValueError('Only main or stable release tags publish images.')
    elif event == 'workflow_dispatch':
        release = image_tag
        moving = push_latest
    else:
        raise ValueError('This event must not publish container images.')
    if release and not STABLE_TAG.fullmatch(release):
        raise ValueError('Release tags must be vX.Y or vX.Y.Z; snapshot/custom tags are not published.')
    if not release and not moving:
        raise ValueError('No image tags selected. Set image_tag or push_latest.')
    full, tiny = [], []
    if moving:
        full.extend(f'{repo}:latest' for repo in REGISTRIES)
        tiny.extend(f'{repo}:latest_tiny' for repo in REGISTRIES)
    if release:
        full.extend(f'{repo}:{release}' for repo in REGISTRIES)
        tiny.extend(f'{repo}:{release}_tiny' for repo in REGISTRIES)
    return {'baked_tags': full, 'tiny_tags': tiny, 'release_tag': release,
            'image_version': release.removeprefix('v') if release else 'snapshot'}


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def add_source_plan(plan: dict, revision: str, run_id: str, attempt: str) -> dict:
    if not re.fullmatch(r'[a-f0-9]{40}', revision) or not re.fullmatch(r'\d+', run_id) or not re.fullmatch(r'\d+', attempt):
        raise ValueError('Source identity requires the exact Git commit and numeric workflow run/attempt.')
    identity = f'sources-{revision}-{run_id}-{attempt}'
    tags = [f'{repo}:{identity}' for repo in REGISTRIES]
    if any(ref.endswith(':latest') for ref in plan['baked_tags']):
        tags.extend(f'{repo}:latest_sources' for repo in REGISTRIES)
    if plan['release_tag']:
        tags.extend(f"{repo}:{plan['release_tag']}_sources" for repo in REGISTRIES)
    return {**plan, 'source_tags': tags, 'source_image': tags[0]}


def check_release_checkout(plan: dict):
    if not plan['release_tag']:
        return
    tagged = run('git', 'rev-parse', '--verify', f"refs/tags/{plan['release_tag']}^{{commit}}")
    head = run('git', 'rev-parse', 'HEAD')
    if tagged.returncode or head.returncode or tagged.stdout.strip() != head.stdout.strip():
        raise ValueError('The selected commit must match the existing stable Git tag. Create/check the release tag first.')


def check_unpublished(plan: dict):
    """Never overwrite an existing stable registry tag, including partial releases."""
    refs = plan['baked_tags'] + plan['tiny_tags'] if plan['release_tag'] else []
    for ref in refs + plan.get('source_tags', []):
        if ref.endswith((':latest', ':latest_tiny', ':latest_sources')):
            continue
        result = run('docker', 'buildx', 'imagetools', 'inspect', ref)
        if result.returncode == 0:
            raise ValueError(f'Immutable release tag already exists: {ref}')
        message = (result.stderr + result.stdout).lower()
        if not any(token in message for token in ('not found', 'manifest unknown', 'manifest_unknown')):
            raise RuntimeError(f'Cannot establish that {ref} is absent; check registry credentials/connectivity.')


def inspect_digest(ref: str) -> str:
    result = run('docker', 'buildx', 'imagetools', 'inspect', ref)
    if result.returncode:
        raise RuntimeError(f'Cannot inspect published image: {ref}')
    match = re.search(r'^Digest:\s+(sha256:[a-f0-9]{64})\s*$', result.stdout, re.M)
    if not match:
        raise RuntimeError(f'No top-level OCI digest reported for {ref}')
    return match[1]


def verify_publication(plan: dict, full_digest: str, tiny_digest: str, source_digest: str = '') -> list[dict]:
    records = []
    variants = [('baked_tags', full_digest), ('tiny_tags', tiny_digest)]
    if plan.get('source_tags'):
        variants.append(('source_tags', source_digest))
    if any(not DIGEST.fullmatch(expected) for _, expected in variants):
        raise ValueError('Build action did not report a valid OCI digest.')
    for key, expected in variants:
        for ref in plan[key]:
            actual = ''
            for attempt in range(4):
                try:
                    actual = inspect_digest(ref)
                    if actual == expected:
                        break
                except RuntimeError:
                    if attempt == 3:
                        raise
                if attempt < 3:
                    time.sleep(2 ** attempt)
            if actual != expected:
                raise RuntimeError(f'Registry digest differs from the build result: {ref}')
            records.append({'image': ref, 'digest': actual, 'pinned': f'{ref}@{actual}'})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-existing', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    output = Path('.ci-build')
    output.mkdir(exist_ok=True)
    plan_file = output / 'image-plan.json'
    if args.verify:
        plan = json.loads(plan_file.read_text(encoding='utf-8'))
        records = verify_publication(plan, os.environ['BAKED_DIGEST'], os.environ['TINY_DIGEST'], os.getenv('SOURCE_DIGEST', ''))
        (output / 'published-images.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
        summary = '\n'.join(f"- `{item['pinned']}`" for item in records)
        if os.getenv('GITHUB_STEP_SUMMARY'):
            with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as stream:
                stream.write('## Published and verified container indexes\n\n' + summary + '\n')
        print(summary)
        return
    plan = plan_images(os.environ['GITHUB_EVENT_NAME'], os.environ['GITHUB_REF'],
                       os.getenv('INPUT_IMAGE_TAG', ''), os.getenv('INPUT_PUSH_LATEST', '') == 'true')
    revision = run('git', 'rev-parse', 'HEAD')
    if revision.returncode:
        raise RuntimeError('Cannot determine checked-out commit.')
    plan = add_source_plan(plan, revision.stdout.strip(), os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_RUN_ATTEMPT'])
    check_release_checkout(plan)
    if args.check_existing:
        check_unpublished(plan)
    plan.update(vcs_ref=revision.stdout.strip(),
                build_date=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    plan_file.write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    if os.getenv('GITHUB_OUTPUT'):
        with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as stream:
            for key in ('baked_tags', 'tiny_tags', 'source_tags'):
                stream.write(f'{key}<<QWEN_IMAGE_TAGS\n' + '\n'.join(plan[key]) + '\nQWEN_IMAGE_TAGS\n')
            for key in ('image_version', 'vcs_ref', 'build_date', 'source_image'):
                stream.write(f'{key}={plan[key]}\n')
    print(json.dumps(plan, indent=2))


if __name__ == '__main__':
    main()
