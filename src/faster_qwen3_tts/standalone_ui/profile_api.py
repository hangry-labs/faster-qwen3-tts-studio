"""Audio-backed voice library with immutable creation assets and editable metadata."""
from __future__ import annotations

import asyncio
import json
import subprocess

from fastapi import File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from .profiles import public_profile


def portrait_bytes(content):
    """Normalize explicitly uploaded raster portraits to a bounded lossless WebP."""
    png = content.startswith(b'\x89PNG\r\n\x1a\n')
    jpeg = content.startswith(b'\xff\xd8\xff')
    webp = content[:4] == b'RIFF' and content[8:12] == b'WEBP'
    if not content or len(content) > 5 * 1024 * 1024 or not (png or jpeg or webp):
        raise ValueError('Choose a PNG, JPEG or WebP portrait up to 5 MB.')
    try:
        result = subprocess.run(['ffmpeg', '-v', 'error', '-max_alloc', '67108864',
            '-protocol_whitelist', 'pipe', '-threads', '1', '-f', 'image2pipe',
            '-max_pixels', '25000000', '-i', 'pipe:0', '-frames:v', '1',
            '-vf', 'scale=100:100:force_original_aspect_ratio=increase,crop=100:100,format=bgra',
            '-c:v', 'libwebp', '-lossless', '1', '-threads', '1', '-f', 'webp', 'pipe:1'],
            input=content, capture_output=True, timeout=15)
        if result.returncode or not result.stdout:
            raise ValueError('Portrait could not be decoded. Use an image up to 25 megapixels.')
        return result.stdout
    except subprocess.TimeoutExpired as exc:
        raise ValueError('Portrait processing timed out. Choose a smaller image.') from exc


def attach_profiles(router, store, canonical_audio):
    def profile_list(q: str = ''):
        needle = q.strip().casefold()
        records = [public_profile(v) for v in store.list()]
        if needle:
            records = [v for v in records if needle in ' '.join([
                v['name'], v['description'], v['language'], *v['tags']]).casefold()]
        return {'object': 'list', 'data': records, 'count': len(records)}
    router.add_api_route('/tts/voice-profiles', profile_list, methods=['GET'])

    def metadata(name, ref_text, language, description, tags, recipe, profile_type):
        from .speech import language as resolve_language
        result = {'name': name}
        for key, value in [('transcript', ref_text), ('description', description), ('profile_type', profile_type)]:
            if value is not None:
                result[key] = value
        if language is not None:
            result['language'] = resolve_language(language or 'English')
        if tags is not None:
            result['tags'] = json.loads(tags)
        if recipe is not None:
            result['recipe'] = json.loads(recipe)
        return result

    async def read_assets(original_audio, processed_audio, design_audio, portrait):
        assets = {}
        for key, upload in [('original', original_audio), ('processed', processed_audio), ('source', design_audio)]:
            if upload is not None:
                assets[key] = await canonical_audio(upload, preserve_float=True)
        if portrait is not None:
            content = await portrait.read(5 * 1024 * 1024 + 1)
            assets['portrait'] = await asyncio.to_thread(portrait_bytes, content)
        return assets

    @router.post('/tts/voice-profiles')
    async def save_profile(name: str = Form(...), profile_type: str = Form('clone'), ref_text: str = Form(''),
        language: str = Form('English'), description: str = Form(''), tags: str = Form('[]'), recipe: str = Form('{}'),
        replace: bool = Form(False), reference_audio: UploadFile = File(...),
        original_audio: UploadFile | None = File(None), processed_audio: UploadFile | None = File(None),
        design_audio: UploadFile | None = File(None), portrait: UploadFile | None = File(None)):
        values = metadata(name, ref_text, language, description, tags, recipe, profile_type)
        assets = await read_assets(original_audio, processed_audio, design_audio, portrait)
        records = store.commit([(values, await canonical_audio(reference_audio, preserve_float=True), replace, assets)])
        return public_profile(records[name.strip()])

    @router.put('/tts/voice-profiles/{identity}')
    async def edit_profile(identity: str, name: str = Form(...), ref_text: str | None = Form(None),
        language: str | None = Form(None), description: str | None = Form(None), tags: str | None = Form(None),
        recipe: str | None = Form(None), profile_type: str | None = Form(None), replace_audio: bool = Form(False),
        clear_portrait: bool = Form(False), reference_audio: UploadFile | None = File(None),
        original_audio: UploadFile | None = File(None), processed_audio: UploadFile | None = File(None),
        design_audio: UploadFile | None = File(None), portrait: UploadFile | None = File(None)):
        if reference_audio is not None and not replace_audio:
            raise ValueError('Confirm replace_audio=true before replacing a saved voice recording.')
        if reference_audio is None and any(v is not None for v in (original_audio, processed_audio, design_audio)):
            raise ValueError('Creation audio assets require a confirmed replacement recording.')
        if clear_portrait and portrait is not None:
            raise ValueError('Choose either a new portrait or clear_portrait.')
        values = metadata(name, ref_text, language, description, tags, recipe, profile_type)
        assets = await read_assets(original_audio, processed_audio, design_audio, portrait)
        if clear_portrait:
            assets['portrait'] = None
        audio = await canonical_audio(reference_audio, preserve_float=True) if reference_audio is not None else None
        return public_profile(store.update(identity, values, audio, assets))

    @router.get('/tts/voice-profiles/{identity}/{variant}')
    def profile_asset(identity: str, variant: str):
        try:
            voice = store.resolve(identity)
            content = store.audio(voice) if variant == 'audio' else store.asset(voice, 'source' if variant == 'design-audio' else variant)
        except (ValueError, FileNotFoundError) as exc:
            raise HTTPException(404, str(exc)) from exc
        return Response(content, media_type='image/webp' if variant == 'portrait' else 'audio/wav',
                        headers={'Cache-Control': 'no-store'})

    @router.delete('/tts/voice-profiles/{identity}')
    def remove_profile(identity: str):
        return {'deleted': True, 'id': store.delete(identity)['id']}

    return profile_list
