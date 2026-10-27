"""Gallery data integrity, reproducible regeneration and packaged HTTP media."""
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

from fastapi.testclient import TestClient
import pytest

from scripts import generate_gallery
from faster_qwen3_tts.standalone_ui import server
from faster_qwen3_tts.standalone_ui.runtime import StudioEngine

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not (ROOT/'examples/assets/manifest.json').exists(),reason='Listening gallery ships in repository/images')
def test_published_gallery_files_match_generation_manifest():
    root = ROOT/'examples'
    definitions = json.loads((root/'definitions.json').read_text(encoding='utf-8'))
    manifest = json.loads((root/'assets/manifest.json').read_text(encoding='utf-8'))
    definition_bytes = (root/'definitions.json').read_bytes().replace(b'\r\n',b'\n')
    assert manifest['definitions_sha256'] == hashlib.sha256(definition_bytes).hexdigest()
    assert len(definitions['voices']) == len(manifest['voices']) == 10
    assert {row['language'] for row in manifest['languages']} == set(server.LANGUAGES)-{'Auto'}
    samples = [reference for voice in manifest['voices'] for reference in voice['references'].values()]
    assert len(samples) == 100
    samples += manifest.get('featured_examples',[])
    for language in manifest['languages']:
        assert [len(language[key]) for key in ['random','intro','clone']] == [10,3,1]
        samples += [sample for key in ['random','intro','clone'] for sample in language[key]]
    assert not list((root/'assets').rglob('*.mp3'))
    assert {sample['file'] for sample in samples} == {
        path.relative_to(root/'assets').as_posix() for extension in ['*.flac','*.opus']
        for path in (root/'assets').rglob(extension)}
    for sample in samples:
        path = root/'assets'/sample['file']
        assert path.resolve().is_relative_to((root/'assets').resolve())
        content = path.read_bytes()
        assert len(content) == sample['bytes']
        assert hashlib.sha256(content).hexdigest() == sample['sha256']
        if path.suffix == '.opus':
            assert sample['recipe']['encoding'] == generate_gallery.OPUS_ENCODING
            assert content.startswith(b'OggS') and b'OpusHead' in content[:100]
        assert 0 < sample['duration_seconds'] < 50
        if sample['recipe']['request']['model'] == 'auto':
            assert sample['recipe']['models'] == manifest['models']
        else:
            assert sample['recipe']['request']['model'] in {value['id'] for value in manifest['models'].values()}
    assert (root/'voices.js').read_text(encoding='utf-8').split('window.EXAMPLE_MANIFEST = ',1)[1].strip() == json.dumps(manifest,ensure_ascii=False,indent=2)+';'


@pytest.mark.parametrize('newline',['\n','\r\n'])
def test_definitions_checksum_is_portable_but_detects_content_edits(tmp_path,newline):
    text = '{\n  "text": "Hello 世界"\n}\n'
    path = tmp_path/'definitions.json'
    path.write_bytes(text.replace('\n',newline).encode('utf-8'))
    assert generate_gallery.definitions_checksum(path) == hashlib.sha256(text.encode('utf-8')).hexdigest()
    path.write_bytes(text.replace('Hello','Goodbye').replace('\n',newline).encode('utf-8'))
    assert generate_gallery.definitions_checksum(path) != hashlib.sha256(text.encode('utf-8')).hexdigest()


def test_featured_json_builds_declared_voices_with_escaped_text_and_exact_pauses():
    definitions = {'voices':[dict(id='narrator',design=dict(instruct='Warm & clear',text='A < B.',seed=12))]}
    entry = dict(characters=[dict(name='Mara',voice='narrator')],turns=[
        dict(character='Mara',text='Hello & welcome.',break_after_ms=300),
        dict(character='Mara',text='A < B.')])
    document = ET.fromstring(generate_gallery.feature_document(definitions,entry))
    ns = {'s':'http://www.w3.org/2001/10/synthesis','h':'https://hangrylabs.app/ns/ssml-h/1.0'}
    voice = document.find('.//h:voice-definition',ns)
    assert voice.attrib == {'name':'Mara','scope':'request','seed':'12'}
    assert voice.find('h:description',ns).text == 'Warm & clear'
    assert [node.text for node in document.findall('s:voice',ns)] == ['Hello & welcome.','A < B.']
    assert document.find('s:break',ns).attrib['time'] == '300ms'


def test_resume_requires_matching_request_revision_reference_and_encoded_content(tmp_path,monkeypatch):
    calls = []
    monkeypatch.setattr(generate_gallery,'generate',lambda *args: calls.append(args) or b'wave')
    monkeypatch.setattr(generate_gallery,'encode',lambda *args:(b'encoded',1.5))
    request = dict(model='base',text='Hello.',seed=123)
    sample = generate_gallery.render('http://studio',tmp_path,{},'english/01.opus',request,{'base':'r1'},b'reference')
    previous = {sample['file']:sample}
    generate_gallery.render('http://studio',tmp_path,previous,sample['file'],request,{'base':'r1'},b'reference')
    assert len(calls) == 1
    generate_gallery.render('http://studio',tmp_path,previous,sample['file'],request,{'base':'r2'},b'reference')
    generate_gallery.render('http://studio',tmp_path,previous,sample['file'],request,{'base':'r1'},b'new reference')
    generate_gallery.render('http://studio',tmp_path,previous,sample['file'],dict(request,seed=124),{'base':'r1'},b'reference')
    monkeypatch.setitem(generate_gallery.OPUS_ENCODING,'bitrate',96000)
    generate_gallery.render('http://studio',tmp_path,previous,sample['file'],request,{'base':'r1'},b'reference')
    monkeypatch.setitem(generate_gallery.OPUS_ENCODING,'bitrate',64000)
    (tmp_path/sample['file']).write_bytes(b'corrupt')
    generate_gallery.render('http://studio',tmp_path,previous,sample['file'],request,{'base':'r1'},b'reference')
    assert len(calls) == 6


def test_gallery_routes_serve_html_json_and_seekable_audio_without_inference(tmp_path,monkeypatch):
    gallery = tmp_path/'gallery'
    gallery.mkdir()
    (gallery/'index.html').write_text('<h1>Gallery</h1>')
    (gallery/'definitions.json').write_text('{"voices":[]}')
    (gallery/'clip.opus').write_bytes(b'0123456789')
    monkeypatch.setattr(server,'GALLERY',gallery)
    engine = StudioEngine()
    with TestClient(server.create_app(engine,tmp_path/'operator')) as client:
        assert client.get('/examples/').status_code == 200
        assert client.get('/examples/definitions.json').json() == {'voices':[]}
        response = client.get('/examples/clip.opus',headers={'Range':'bytes=2-5'})
        assert response.status_code == 206 and response.content == b'2345'
        assert response.headers['content-type'] == 'audio/ogg'
        assert client.get('/examples/../settings.json').status_code == 404
        assert engine.model is None and not engine.admissions
