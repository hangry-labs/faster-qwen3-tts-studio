"""Explicit voice references with atomic, multi-profile publication.

Old per-directory Studio profiles remain readable. New snapshots publish through
one index replacement so a failed design request cannot leave half its voices.
"""
from __future__ import annotations

import json
import re
import shutil
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

ASSET_FILES = {'original': 'original.wav', 'processed': 'processed.wav',
               'source': 'source.wav', 'portrait': 'portrait.webp'}


def public_profile(record):
    value = {k: v for k, v in record.items() if k != 'audio_folder' and not k.startswith('_')}
    base = f"/tts/voice-profiles/{record['id']}"
    return {**value, 'ref_text': record.get('transcript', ''),
            'profile_type': record.get('profile_type', 'clone'),
            'language': record.get('language', 'English'), 'description': record.get('description', ''),
            'tags': record.get('tags', []), 'recipe': record.get('recipe', {}),
            **{f'{key}_url': f'{base}/{key}' if key in record.get('_asset_folders', {}) else None
               for key in ASSET_FILES}}


class VoiceStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()

    def list(self):
        with self.lock:
            index = self.root / 'index.json'
            if index.exists():
                return json.loads(index.read_text(encoding='utf-8'))
            return [json.loads(p.read_text(encoding='utf-8')) for p in sorted(self.root.glob('*/voice.json'))]

    def resolve(self, identity):
        candidates = [v for v in self.list() if v['id'] == identity or v['name'].casefold() == identity.casefold()]
        if len(candidates) != 1:
            raise ValueError(f"Voice '{identity}' is {'ambiguous' if candidates else 'not saved'}. Choose a saved id or a unique name.")
        return candidates[0]

    def audio(self, voice):
        folder = voice.get('audio_folder', voice['id'])
        if not re.fullmatch(r'[a-f0-9]{32}', folder):
            raise ValueError('Invalid saved voice audio.')
        return (self.root / folder / 'audio.wav').read_bytes()

    def asset(self, voice, kind):
        if kind not in ASSET_FILES:
            raise ValueError('Unknown voice asset.')
        folder = voice.get('_asset_folders', {}).get(kind)
        if not folder or not re.fullmatch(r'[a-f0-9]{32}', folder):
            raise FileNotFoundError('This voice has no saved ' + kind + '.')
        return (self.root / folder / ASSET_FILES[kind]).read_bytes()

    @staticmethod
    def _metadata(metadata):
        name = metadata['name'].strip()
        if not name or len(name) > 256 or len(metadata.get('transcript', '')) > 4000:
            raise ValueError('Provide a voice name up to 256 characters and transcript up to 4000 characters.')
        tags = metadata.get('tags', [])
        if not isinstance(tags, list) or len(tags) > 12 or any(not isinstance(t, str) or len(t) > 32 for t in tags):
            raise ValueError('Use up to 12 tags, each up to 32 characters.')
        normalized, seen = [], set()
        for tag in tags:
            tag = ' '.join(tag.split())
            if tag and tag.casefold() not in seen:
                normalized.append(tag)
                seen.add(tag.casefold())
        recipe = metadata.get('recipe', {})
        if not isinstance(recipe, dict) or len(json.dumps(recipe, allow_nan=False)) > 16000:
            raise ValueError('Recipe must be a JSON object up to 16000 characters.')
        if len(metadata.get('description', '')) > 1500:
            raise ValueError('Description must be up to 1500 characters.')
        if metadata.get('profile_type', 'clone') not in {'clone', 'reference', 'design'}:
            raise ValueError('Save an audio-backed clone, reference or design profile.')
        return {**metadata, 'name': name, 'tags': normalized}

    def _publish(self, records):
        temporary = self.root / ('.index-' + uuid.uuid4().hex)
        try:
            temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(self.root / 'index.json')
        finally:
            temporary.unlink(missing_ok=True)

    def commit(self, pending):
        """Items: metadata, WAV bytes, replace permission, optional asset changes.

        Assets are immutable snapshots. Missing keys retain existing assets; None
        explicitly clears one. Metadata-only updates do not copy or replace audio.
        """
        with self.lock:
            records = self.list()
            created, result = [], {}
            try:
                for item in pending:
                    metadata, audio, replace = item[:3]
                    assets = item[3] if len(item) > 3 else {}
                    if audio is not None:
                        assets = {'original': audio, 'processed': None, 'source': None, **assets}
                    metadata = self._metadata(metadata)
                    name = metadata['name']
                    target_id = metadata.get('id')
                    matches = [v for v in records if v['name'].casefold() == name.casefold() or (target_id and v['id'] == target_id)]
                    if matches and (not replace or len(matches) != 1):
                        raise ValueError(f"Voice '{name}' already exists. Explicit replacement is required.")
                    existing = matches[0] if matches else None
                    voice_id = existing['id'] if existing else uuid.uuid4().hex
                    if audio is None and not existing:
                        raise ValueError('New voices need reference audio.')
                    folder_id = (existing or {}).get('audio_folder', voice_id)
                    asset_folders = dict((existing or {}).get('_asset_folders', {}))
                    if audio is not None or assets:
                        folder = self.root / uuid.uuid4().hex
                        folder.mkdir()
                        created.append(folder)
                        if audio is not None:
                            folder_id = folder.name
                            (folder / 'audio.wav').write_bytes(audio)
                        for kind, content in assets.items():
                            if kind not in ASSET_FILES:
                                raise ValueError('Unknown voice asset.')
                            if content is None:
                                asset_folders.pop(kind, None)
                            else:
                                (folder / ASSET_FILES[kind]).write_bytes(content)
                                asset_folders[kind] = folder.name
                    record = {**metadata, 'name': name, 'id': voice_id, 'audio_folder': folder_id,
                              '_asset_folders': asset_folders,
                              'audio_url': f'/studio/voices/{voice_id}/audio',
                              'updated_at': datetime.now(UTC).isoformat(),
                              'created_at': (existing or {}).get('created_at', datetime.now(UTC).isoformat())}
                    if existing:
                        records.remove(existing)
                        record['_audio_versions'] = list(dict.fromkeys([
                            *existing.get('_audio_versions', []), existing.get('audio_folder', existing['id']),
                            *existing.get('_asset_folders', {}).values()]))
                    records.append(record)
                    result[name] = record
                self._publish(records)
            except Exception:
                for folder in created:
                    shutil.rmtree(folder)
                raise
            # Audio snapshots may be held by an in-flight reader. Leave old versions
            # until explicit deletion rather than racing a synthesis request.
            return result

    def update(self, identity, metadata, audio=None, assets=None):
        with self.lock:
            old = self.resolve(identity)
            merged = {**old, **metadata}
            if audio is not None and '_openai_type' not in metadata:
                # A replacement recording has its own provenance. Do not label
                # uploaded audio as the original prompt-generated resource.
                for key in ('_openai_type', 'prompt', 'consent'):
                    merged.pop(key, None)
            return self.commit([(merged, audio, True, assets or {})])[merged['name'].strip()]

    def delete(self, identity):
        with self.lock:
            old = self.resolve(identity)
            self._publish([v for v in self.list() if v['id'] != old['id']])
            # Metadata is removed atomically; references already read by a request
            # remain request-owned. Clean all generations belonging to this id.
            for identity in set([old.get('audio_folder', old['id']), *old.get('_audio_versions', []),
                                 *old.get('_asset_folders', {}).values()]):
                folder = self.root / identity
                if folder.is_dir() and re.fullmatch(r'[a-f0-9]{32}', folder.name):
                    shutil.rmtree(folder)
            return old
