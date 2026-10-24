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

    def _publish(self, records):
        temporary = self.root / ('.index-' + uuid.uuid4().hex)
        try:
            temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(self.root / 'index.json')
        finally:
            temporary.unlink(missing_ok=True)

    def commit(self, pending):
        """pending items: metadata, WAV bytes, replace-existing permission."""
        with self.lock:
            records = self.list()
            created, result = [], {}
            try:
                for metadata, audio, replace in pending:
                    name = metadata['name'].strip()
                    if not name or len(name) > 80 or len(metadata.get('transcript', '')) > 4000:
                        raise ValueError('Provide a voice name up to 80 characters and transcript up to 4000 characters.')
                    target_id = metadata.get('id')
                    matches = [v for v in records if v['name'].casefold() == name.casefold() or (target_id and v['id'] == target_id)]
                    if matches and (not replace or len(matches) != 1):
                        raise ValueError(f"Voice '{name}' already exists. Explicit replacement is required.")
                    existing = matches[0] if matches else None
                    voice_id = existing['id'] if existing else uuid.uuid4().hex
                    folder_id = uuid.uuid4().hex
                    folder = self.root / folder_id
                    folder.mkdir()
                    created.append(folder)
                    (folder / 'audio.wav').write_bytes(audio)
                    record = {**metadata, 'name': name, 'id': voice_id, 'audio_folder': folder_id,
                              'audio_url': f'/studio/voices/{voice_id}/audio',
                              'created_at': (existing or {}).get('created_at', datetime.now(UTC).isoformat())}
                    if existing:
                        records.remove(existing)
                        record['_audio_versions'] = list(dict.fromkeys([
                            *existing.get('_audio_versions', []), existing.get('audio_folder', existing['id'])]))
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

    def update(self, identity, metadata, audio=None):
        with self.lock:
            old = self.resolve(identity)
            merged = {**old, **metadata}
            return self.commit([(merged, audio if audio is not None else self.audio(old), True)])[merged['name']]

    def delete(self, identity):
        with self.lock:
            old = self.resolve(identity)
            self._publish([v for v in self.list() if v['id'] != old['id']])
            # Metadata is removed atomically; references already read by a request
            # remain request-owned. Clean all generations belonging to this id.
            for identity in [old.get('audio_folder', old['id']), *old.get('_audio_versions', [])]:
                folder = self.root / identity
                if folder.is_dir() and re.fullmatch(r'[a-f0-9]{32}', folder.name):
                    shutil.rmtree(folder)
            return old
