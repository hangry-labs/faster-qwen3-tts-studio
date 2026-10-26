"""OpenAI voice resources backed by the Studio's atomic audio asset store."""
from __future__ import annotations

import asyncio
from datetime import datetime, UTC
import io
import re
import uuid
from typing import Literal

from fastapi import HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from starlette.datastructures import UploadFile
import soundfile as sf

from .profiles import VoiceStore
from .speech import NATIVE_LANGUAGES, VOICE_ALIASES, SpeechRequest, language


class VoiceCreate(BaseModel):
    model_config = ConfigDict(extra='ignore')
    name: str = Field(min_length=1, max_length=256)
    type: Literal['audio_sample', 'prompt'] = 'audio_sample'
    consent: str | None = Field(default=None, max_length=100)
    prompt: str | None = Field(default=None, min_length=1, max_length=2000)
    script_hint: str | None = Field(default=None, min_length=1, max_length=2000)
    model: str = 'auto'
    # Local extensions: exact reference words and target speech language.
    ref_text: str = Field(default='', max_length=4000)
    language: str = 'English'

    @field_validator('name', 'prompt', 'script_hint')
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():
            raise ValueError('Must not be blank.')
        return value.strip() if value is not None else None


class ConsentCreate(BaseModel):
    model_config = ConfigDict(extra='ignore')
    name: str = Field(min_length=1, max_length=256)
    language: str = Field(min_length=1, max_length=100, pattern=r'^[A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*$')

    @field_validator('name')
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError('Must not be blank.')
        return value.strip()


class ConsentUpdate(BaseModel):
    model_config = ConfigDict(extra='ignore')
    name: str = Field(min_length=1, max_length=256)

    @field_validator('name')
    @classmethod
    def nonblank(cls, value):
        return ConsentCreate.nonblank(value)


def voice_object(record):
    timestamp = record.get('created_at')
    parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else None
    created = int((parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)).timestamp()) if parsed else 0
    result = {'id': record['id'], 'object': 'audio.voice', 'created_at': created,
              'name': record['name'], 'type': record.get('_openai_type', 'audio_sample')}
    if result['type'] == 'prompt':
        result['prompt'] = record['prompt']
    return result


def consent_object(record):
    return {'id': 'cons_' + record['id'], 'object': 'audio.voice_consent',
            'created_at': voice_object(record)['created_at'],
            'name': record['label'], 'language': record['language']}


async def fields(request, model, consume):
    """Bound metadata and close multipart files even when validation fails."""
    try:
        if request.headers.get('content-type', '').split(';')[0].strip() == 'application/json':
            content = bytearray()
            async for block in request.stream():
                content.extend(block)
                if len(content) > 16384:
                    raise HTTPException(400, 'Voice metadata must fit 16 KiB.')
            return await consume(model.model_validate_json(content), None)
        async with request.form(max_files=1, max_fields=16, max_part_size=16384) as form:
            values = {key: value for key, value in form.items() if not isinstance(value, UploadFile)}
            return await consume(model.model_validate(values), form)
    except ValidationError as exc:
        raise HTTPException(400, str(exc)) from exc


def creation_schema():
    schema = VoiceCreate.model_json_schema()
    form = {**schema, 'properties': {**schema['properties'], 'audio_sample': {'type': 'string', 'format': 'binary'}}}
    return {'requestBody': {'required': True, 'content': {
        'application/json': {'schema': schema}, 'multipart/form-data': {'schema': form}}}}


def reference_wav(samples):
    output = io.BytesIO()
    sf.write(output, samples, 24000, format='WAV', subtype='FLOAT')
    return output.getvalue()


def attach_openai_voices(router, store, canonical_audio, prepare_generation, complete):
    # Consent recordings are separate resources, never selectable as voices.
    # Reuse the atomic asset machinery, not a second voice registry.
    consents = VoiceStore(store.root.parent / 'voice-consents')

    def consent_record(identity):
        if not re.fullmatch(r'cons_[a-f0-9]{32}', identity):
            raise HTTPException(404, 'Consent recording not found.')
        try:
            return consents.resolve(identity[5:])
        except ValueError as exc:
            raise HTTPException(404, 'Consent recording not found.') from exc

    def available_name(name):
        if name.casefold() in {n.casefold() for n in NATIVE_LANGUAGES} or name.casefold() in VOICE_ALIASES:
            raise HTTPException(409, 'Choose a name different from a built-in voice or alias.')
        if any(v['name'].casefold() == name.casefold() or v['id'] == name for v in store.list()):
            raise HTTPException(409, 'A voice with this name already exists. Use the native API for explicit replacement.')

    def save_voice(values, content):
        try:
            with consents.lock, store.lock:
                if values.get('consent'):
                    consent_record(values['consent'])
                available_name(values['name'])
                return store.commit([(values, content, False)])[values['name']]
        except OSError as exc:
            raise HTTPException(500, 'Could not save the voice.') from exc

    @router.post('/v1/audio/voices', openapi_extra=creation_schema())
    async def create_voice(request: Request):
        async def create(payload, form):
            await asyncio.to_thread(available_name, payload.name)
            target_language = language(payload.language)
            values = {'name': payload.name, 'language': target_language, '_openai_type': payload.type}
            if payload.type == 'audio_sample':
                if payload.prompt is not None or payload.script_hint is not None or payload.model != 'auto':
                    raise HTTPException(400, 'prompt, script_hint and model apply to type=prompt.')
                if not payload.consent:
                    raise HTTPException(400, 'Provide the ID of a locally uploaded consent recording.')
                await asyncio.to_thread(consent_record, payload.consent)
                sample = form.get('audio_sample') if form is not None else None
                if not isinstance(sample, UploadFile):
                    raise HTTPException(400, 'Provide audio_sample as a multipart file.')
                content = await canonical_audio(sample, preserve_float=True)
                values.update(consent=payload.consent, transcript=payload.ref_text, profile_type='clone')
            else:
                if not payload.prompt:
                    raise HTTPException(400, 'Provide prompt for type=prompt.')
                if payload.consent or (form is not None and form.get('audio_sample') is not None):
                    raise HTTPException(400, 'Choose a prompt or an audio sample, not both.')
                model = payload.model
                # Qwen uses its own checkpoint IDs; OpenAI model revisions do not
                # describe weights available in this server.
                if model != 'auto' and model != 'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign':
                    raise HTTPException(400, 'Choose model=auto or the Qwen VoiceDesign checkpoint.')
                script = payload.script_hint or ('Hello. This is a sample of my voice. I speak clearly and naturally, '
                                                 'with a comfortable and steady rhythm.')
                speech = SpeechRequest(text=script, mode='design', model=model, instruct=payload.prompt,
                                       language=target_language, output_format='wav', max_new_tokens=600)
                prepared = await prepare_generation(speech)
                result = await complete(prepared, request)
                if len(result['audio']) > 120 * 24000:
                    raise HTTPException(400, 'The voice sample exceeds two minutes. Choose a shorter script_hint.')
                content = await asyncio.to_thread(reference_wav, result['audio'])
                values.update(profile_type='design', transcript=script, prompt=payload.prompt,
                    recipe={'version': 1, 'workflow': 'design', 'settings': {'instruct': payload.prompt,
                            'text': script, 'model': prepared.default.model, 'seed': prepared.seed}})
            if await request.is_disconnected():
                raise HTTPException(499, 'Client disconnected.')
            return voice_object(await asyncio.to_thread(save_voice, values, content))
        return await fields(request, VoiceCreate, create)

    @router.delete('/v1/audio/voices/{voice_id}')
    def delete_voice(voice_id: str):
        with store.lock:
            if not any(v['id'] == voice_id for v in store.list()):
                raise HTTPException(404, 'Saved voice ID not found.')
            try:
                store.delete(voice_id)
            except OSError as exc:
                raise HTTPException(500, 'Could not delete the voice.') from exc
        return {'id': voice_id, 'deleted': True, 'object': 'audio.voice.deleted'}

    consent_schema = ConsentCreate.model_json_schema()
    consent_schema['properties']['recording'] = {'type': 'string', 'format': 'binary'}
    consent_schema['required'].append('recording')

    @router.post('/v1/audio/voice_consents', openapi_extra={'requestBody': {'required': True,
        'content': {'multipart/form-data': {'schema': consent_schema}}}})
    async def create_consent(request: Request):
        async def create(payload, form):
            recording = form.get('recording') if form is not None else None
            if not isinstance(recording, UploadFile):
                raise HTTPException(400, 'Provide recording as a multipart file.')
            content = await canonical_audio(recording, preserve_float=True)
            values = {'name': uuid.uuid4().hex, 'label': payload.name, 'language': payload.language}
            try:
                result = await asyncio.to_thread(consents.commit, [(values, content, False)])
            except OSError as exc:
                raise HTTPException(500, 'Could not save the consent recording.') from exc
            return consent_object(result[values['name']])
        return await fields(request, ConsentCreate, create)

    @router.get('/v1/audio/voice_consents')
    def list_consents(after: str | None = None, limit: int = Query(default=20, ge=1, le=100)):
        with consents.lock:
            records = consents.list()
            if after is not None:
                record = consent_record(after)
                records = records[records.index(record) + 1:]
            page = [consent_object(v) for v in records[:limit]]
        return {'object': 'list', 'data': page, 'has_more': len(records) > limit,
                'first_id': page[0]['id'] if page else None, 'last_id': page[-1]['id'] if page else None}

    @router.get('/v1/audio/voice_consents/{consent_id}')
    def retrieve_consent(consent_id: str):
        return consent_object(consent_record(consent_id))

    @router.post('/v1/audio/voice_consents/{consent_id}')
    def update_consent(consent_id: str, payload: ConsentUpdate):
        try:
            with consents.lock:
                record = consent_record(consent_id)
                return consent_object(consents.update(record['id'], {'label': payload.name}))
        except OSError as exc:
            raise HTTPException(500, 'Could not update the consent recording.') from exc

    @router.delete('/v1/audio/voice_consents/{consent_id}')
    def delete_consent(consent_id: str):
        try:
            with consents.lock:
                record = consent_record(consent_id)
                consents.delete(record['id'])
        except OSError as exc:
            raise HTTPException(500, 'Could not delete the consent recording.') from exc
        return {'id': consent_id, 'deleted': True, 'object': 'audio.voice_consent'}

    return consents
