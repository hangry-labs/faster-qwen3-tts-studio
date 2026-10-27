"""Generate the static gallery through a running Studio. Requires FFmpeg on PATH.

Definitions include both voice design and reference-guided speech. No operator
settings or saved voices are changed. Completed clips are reused only when their
request, model revisions and reference checksum still match.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.request import urlopen, Request
from xml.sax.saxutils import escape, quoteattr

from scripts.smoke_studio import post


def checksum(content):
    return hashlib.sha256(content).hexdigest()


def definitions_checksum(path):
    # Git checkouts can use LF or CRLF. Hash the same UTF-8/LF text on both hosts.
    return checksum(path.read_text(encoding='utf-8').encode('utf-8'))


def fingerprint(value):
    return checksum(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())


OPUS_ENCODING = {'codec':'opus','container':'ogg','bitrate':64000,'vbr':True,
                 'application':'audio','compression_level':10}


def encode(wave, extension):
    if extension == 'flac':
        codec = ['-c:a','flac']
    elif extension == 'opus':
        codec = ['-c:a','libopus','-b:a',str(OPUS_ENCODING['bitrate']),
                 '-vbr','on' if OPUS_ENCODING['vbr'] else 'off','-application',OPUS_ENCODING['application'],
                 '-compression_level',str(OPUS_ENCODING['compression_level'])]
    else:
        raise ValueError('Gallery audio must be lossless FLAC references or Ogg Opus listening clips.')
    with tempfile.TemporaryDirectory(prefix='qwen-gallery-') as folder:
        output = Path(folder)/('clip.'+extension)
        subprocess.run(['ffmpeg','-v','error','-y','-i','pipe:0','-map_metadata','-1',*codec,str(output)],
                       input=wave, check=True, capture_output=True)
        duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries',
                         'format=duration','-of','default=nw=1:nk=1',str(output)]))
        return output.read_bytes(), round(duration,3)


def generate(base, request, reference=None):
    files = {'reference': ('reference.flac',reference)} if reference is not None else None
    with post(base+'/studio/generate', {'options':json.dumps(request)}, files) as response:
        result = json.load(response)
    # Studio rejects generation-budget/context cutoffs rather than returning a
    # successful response with truncated speech.
    if result['metrics'].get('duration_s',0) <= 0:
        raise RuntimeError('Gallery sample did not contain speech.')
    return base64.b64decode(result['audio_b64'])


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    temporary.replace(path)


def feature_document(definition, entry):
    voices = {voice['id']:voice for voice in definition['voices']}
    lines = ['<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"',
             '       xmlns:h="https://hangrylabs.app/ns/ssml-h/1.0" xml:lang="en-US">',
             '  <metadata><h:extensions version="1.0">']
    names = set()
    for character in entry['characters']:
        names.add(character['name'])
        design = voices[character['voice']]['design']
        lines += ['    <h:voice-definition name='+quoteattr(character['name'])+' scope="request" seed='+quoteattr(str(design['seed']))+'>',
                  '      <h:description>'+escape(design['instruct'])+'</h:description>',
                  '      <h:sample xml:lang="en-US">'+escape(design['text'])+'</h:sample>',
                  '    </h:voice-definition>']
    lines += ['  </h:extensions></metadata>']
    for turn in entry['turns']:
        if turn['character'] not in names:
            raise ValueError('Featured dialogue uses an undeclared character.')
        lines.append('  <voice name='+quoteattr(turn['character'])+'>'+escape(turn['text'])+'</voice>')
        if turn.get('break_after_ms'):
            pause = turn['break_after_ms']
            if not isinstance(pause,int) or not 0 < pause <= 10000:
                raise ValueError('Featured pauses must be from 1 to 10000 milliseconds.')
            lines.append('  <break time="'+str(pause)+'ms"/>')
    return '\n'.join(lines+['</speak>'])+'\n'


def render(base, assets, previous, file, request, revisions, reference=None):
    recipe = dict(request=request, model_revision=revisions[request['model']],
                  reference_sha256=checksum(reference) if reference is not None else None)
    if Path(file).suffix == '.opus':
        recipe['encoding'] = dict(OPUS_ENCODING)
    identity = fingerprint(recipe)
    existing = previous.get(file)
    target = assets/file
    if existing and existing.get('fingerprint') == identity and target.is_file():
        if checksum(target.read_bytes()) == existing.get('sha256'):
            return existing
    print('Generating '+file,flush=True)
    wave = generate(base,request,reference)
    content,duration = encode(wave,target.suffix[1:])
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary = target.with_suffix(target.suffix+'.tmp')
    temporary.write_bytes(content)
    temporary.replace(target)
    return dict(file=file,text=request['text'],recipe=recipe,fingerprint=identity,
                sha256=checksum(content),bytes=len(content),duration_seconds=duration)


def build(args):
    root = args.output
    assets = root/'assets'
    definition = json.loads(args.definitions.read_text(encoding='utf-8'))
    for collection,field in [('voices','id'),('languages','slug')]:
        identifiers = [row[field] for row in definition[collection]]
        if not identifiers or len(set(identifiers)) != len(identifiers) or any(
                not re.fullmatch(r'[a-z][a-z0-9_-]{0,63}',value) for value in identifiers):
            raise ValueError('Use unique lowercase identifiers for gallery '+collection+'.')
    for entry in definition.get('featured',[]):
        if not (root/entry['document']).resolve().is_relative_to(root.resolve()) or not (assets/entry['file']).resolve().is_relative_to(assets.resolve()):
            raise ValueError('Featured files must stay inside the gallery.')
    with urlopen(args.base_url+'/studio/capabilities',timeout=30) as response:
        revisions = {entry['id']:entry['revision'] for entry in json.load(response)['models']}
    manifest_path = assets/'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    previous = {}
    for voice in manifest.get('voices',[]):
        if 'reference' in voice:
            previous[voice['reference']['file']] = voice['reference']
        for reference in voice.get('references',{}).values():
            previous[reference['file']] = reference
    for language in manifest.get('languages',[]):
        for group in ['random','intro','clone']:
            for sample in language.get(group,[]):
                previous[sample['file']] = sample
    manifest.update(schema_version=1,project_name=definition['project_name'],
                    generated_at=datetime.now(timezone.utc).isoformat(),
                    definitions_sha256=definitions_checksum(args.definitions),
                    models={name:dict(id=model,revision=revisions[model]) for name,model in definition['models'].items()})

    def save():
        write_json(manifest_path,manifest)
        meta = {language['slug']:dict(nativeName=language['native_name'],icon=language['icon'])
                for language in definition['languages']}
        js = 'window.LANGUAGE_META = '+json.dumps(meta,ensure_ascii=False,indent=2)+';\n'
        js += 'window.EXAMPLE_MANIFEST = '+json.dumps(manifest,ensure_ascii=False,indent=2)+';\n'
        (root/'voices.js').write_text(js,encoding='utf-8',newline='\n')

    if args.phase in {'all','design'}:
        manifest['voices'] = []
        for voice in definition['voices']:
            output = dict(id=voice['id'],label=voice['label'],design=voice['design'],references={})
            manifest['voices'].append(output)
            for index,language in enumerate(definition['languages']):
                request = dict(definition['generation'], **voice['design'], mode='design',
                               model=definition['models']['design'],non_streaming_mode=True)
                request.update(language=language['language'],text=language.get('reference_text',voice['design']['text']),
                               seed=language.get('design_seeds',{}).get(voice['id'],voice['design']['seed']+100*index))
                file = 'references/'+('' if language['slug']=='english' else language['slug']+'/')+voice['id']+'.flac'
                sample = render(args.base_url,assets,previous,file,request,revisions)
                output['references'][language['slug']] = sample
                if language['slug']=='english':
                    output['reference'] = sample
                save()
    voices = {voice['id']:voice for voice in manifest.get('voices',[])}
    if args.phase in {'all','speech'}:
        for voice in definition['voices']:
            if voice['id'] not in voices or set(voices[voice['id']].get('references',{})) != {lang['slug'] for lang in definition['languages']}:
                raise ValueError('Generate all voice references before the speech phase.')
        manifest['reference_voice'] = definition['reference_voice']
        # Keep partial runs resumable: every finished clip is checkpointed.
        manifest['languages'] = []
        for language in definition['languages']:
            output = {key:language[key] for key in ['slug','language','native_name','icon','intro_text']}
            output.update(random=[],intro=[],clone=[])
            manifest['languages'].append(output)
            jobs = [('random',sample['voice'],sample['text'],sample['seed']) for sample in language['samples']]
            jobs += [('intro',voice,language['intro_text'],8500+i) for i,voice in enumerate(language['intro_voices'])]
            jobs += [('clone',definition['reference_voice'],language['clone_text'],8600)]
            for group,voice_id,text,seed in jobs:
                voice = voices[voice_id]
                reference_sample = voice['reference'] if group=='clone' else voice['references'][language['slug']]
                reference = (assets/reference_sample['file']).read_bytes()
                if checksum(reference) != reference_sample['sha256']:
                    raise ValueError('Saved reference checksum changed. Regenerate the design phase.')
                request = dict(definition['generation'],mode='clone',model=definition['models']['clone'],
                    text=text,language=language['language'],seed=seed,ref_text=reference_sample['text'],
                    xvec_only=False,non_streaming_mode=definition.get('clone_options',{}).get('non_streaming_mode',True))
                file = language['slug']+'/'+group+'/'+str(len(output[group])+1).zfill(2)+'.opus'
                sample = render(args.base_url,assets,previous,file,request,revisions,reference)
                output[group].append(dict(sample,voice_profile=voice_id,reference=reference_sample['file']))
                save()
    if args.phase in {'all','featured'} and definition.get('featured'):
        with urlopen(args.base_url+'/tts/ssml/capabilities',timeout=30) as response:
            processor = json.load(response)['ssml_h']['design_processor']
        if processor['clone_model'] != definition['models']['clone'] or processor['model'] != definition['models']['design']:
            raise ValueError('For the SSML-H gallery scene, select the definition\'s Design and Clone models in System first. No settings were changed.')
        old_featured = {sample['file']:sample for sample in manifest.get('featured_examples',[])}
        manifest['featured_examples'] = []
        for entry in definition['featured']:
            text = feature_document(definition,entry)
            document = root/entry['document']
            document.parent.mkdir(parents=True,exist_ok=True)
            document.write_text(text,encoding='utf-8')
            request = dict(definition['generation'],input_type='ssml-h',text=text,
                           model='auto',language='English',seed=entry['seed'],
                           non_streaming_mode=True,output_format='wav')
            recipe = dict(request=request,models=manifest['models'],encoding=dict(OPUS_ENCODING))
            identity = fingerprint(recipe)
            file = entry['file']
            target = assets/file
            sample = old_featured.get(file)
            if not (sample and sample['fingerprint']==identity and target.is_file() and checksum(target.read_bytes())==sample['sha256']):
                print('Generating '+file,flush=True)
                with urlopen(Request(args.base_url+'/tts/generate',data=json.dumps(request).encode(),
                                     headers={'Content-Type':'application/json'}),timeout=600) as response:
                    content,duration = encode(response.read(),'opus')
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(content)
                sample = dict(file=file,recipe=recipe,fingerprint=identity,sha256=checksum(content),
                              bytes=len(content),duration_seconds=duration)
            manifest['featured_examples'].append(dict(sample,**{key:entry[key] for key in
                ['eyebrow','title','description','label','badge','document']}))
            save()
    save()
    print('Gallery '+args.phase+' phase complete.',flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:7860')
    parser.add_argument('--definitions',type=Path,default=Path('examples/definitions.json'))
    parser.add_argument('--output',type=Path,default=Path('examples'))
    parser.add_argument('--phase',choices=['all','design','speech','featured'],default='all')
    args = parser.parse_args()
    args.base_url = args.base_url.rstrip('/')
    build(args)


if __name__ == '__main__':
    main()
