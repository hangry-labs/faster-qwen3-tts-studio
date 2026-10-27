"""Real ASGI WebSockets: full duplex, transcript use and FIFO cleanup."""
import asyncio
import json
import threading
import time

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
import numpy as np
import pytest

from faster_qwen3_tts.standalone_ui import audio
from faster_qwen3_tts.standalone_ui.profiles import VoiceStore
from faster_qwen3_tts.standalone_ui.runtime import StudioEngine
from faster_qwen3_tts.standalone_ui.server import create_app
from test_live_input import tokenizer

LIVE_MODEL = 'Qwen/Qwen3-TTS-12Hz-1.7B-Base'


class Engine(StudioEngine):
    def __init__(self, tokenizer):
        super().__init__(queue_capacity=1)
        self.tokenizer = tokenizer
        self.requests, self.references = [], []

    def generate_live(self, request, reference, feed, emit):
        with self.session(feed.cancelled, emit):
            self.requests.append(request)
            self.references.append(reference.read_bytes())
            feed.attach(self.tokenizer)
            emit({'type': 'ready', 'initial_text_tokens': 1})
            ids, _ = feed.initial(1)
            offset = 0
            while feed.next_token(offset) is not None:
                offset += 1
                emit({'type': 'chunk', 'audio': np.full(2400,.2,dtype=np.float32), 'sample_rate': 24000})
            emit({'type': 'done', 'seed': request.seed, 'metrics': feed.metrics()})


@pytest.fixture
def api(tmp_path, tokenizer):
    engine = Engine(tokenizer)
    store = VoiceStore(tmp_path/'voices')
    content = audio.wav(np.full(2400,.2,dtype=np.float32))
    voice = store.commit([({'name':'saved voice','transcript':'The exact reference words.'},content,False)])['saved voice']
    with TestClient(create_app(engine,tmp_path)) as client:
        yield client,engine,store,voice['id'],content


def start(socket, voice, **options):
    socket.send_json({'type':'start','voice':voice,'seed':4210,**options})
    return socket.receive_json()


def until(socket, kind):
    while True:
        event=socket.receive()
        if event['type']=='websocket.close':
            raise AssertionError('Connection closed before '+kind)
        if 'bytes' in event:
            if kind=='audio':
                return event['bytes']
            continue
        value=json.loads(event['text'])
        if value['type']==kind:
            return value
        assert value['type']!='error',value


def released(engine):
    for _ in range(100):
        if not engine.admissions and not engine.gate.locked():
            return
        time.sleep(.01)
    raise AssertionError('Live session retained an admission or GPU lease')


def test_audio_arrives_before_finish_with_saved_transcript(api):
    client,engine,store,voice,content=api
    with client.websocket_connect('/tts/live') as socket:
        accepted=start(socket,voice)
        assert accepted['format']=='pcm_s16le' and accepted['seed']==4210
        socket.send_json({'type':'text','text':'Good morning. I left the window open. '})
        assert until(socket,'audio')
        assert engine.requests[-1].ref_text=='The exact reference words.'
        # The worker owns a snapshot even if its saved voice is deleted.
        store.delete(voice)
        socket.send_json({'type':'text','text':'Hello world!'})
        socket.send_json({'type':'finish'})
        done=until(socket,'done')
        assert done['metrics']['input_finished']
        assert engine.references==[content]
    released(engine)


def test_speaker_only_accepts_missing_transcript_and_icl_rejects_it(api):
    client,engine,store,voice,_=api
    store.update(voice,{'transcript':''})
    with client.websocket_connect('/tts/live') as socket:
        assert start(socket,voice)['type']=='error'
    with client.websocket_connect('/tts/live') as socket:
        assert start(socket,voice,xvec_only=True)['type']=='accepted'
        socket.send_json({'type':'text','text':'Hello world!'})
        socket.send_json({'type':'finish'})
        until(socket,'done')
    assert engine.requests[-1].xvec_only
    released(engine)


@pytest.mark.parametrize('payload', [{'type':'text','text':42},{'type':'finish'},
                                    {'type':'bogus'},{'type':'text','text':'x'*4001}])
def test_invalid_input_cancels_worker_and_releases_capacity(api,payload):
    client,engine,_,voice,_=api
    with client.websocket_connect('/tts/live') as socket:
        assert start(socket,voice)['type']=='accepted'
        socket.send_json(payload)
        assert until(socket,'error')['code']=='invalid_input'
    released(engine)


def test_disconnecting_and_cancelling_queued_clients_do_not_leak_admissions(api):
    client,engine,_,voice,_=api
    with client.websocket_connect('/tts/live') as first:
        start(first,voice,input_timeout_s=5)
        first.send_json({'type':'text','text':'Hello world! Good morning. '})
        until(first,'audio')
        with client.websocket_connect('/tts/live') as second:
            assert start(second,voice)['type']=='accepted'
            until(second,'queued')
            with client.websocket_connect('/tts/live') as full:
                assert start(full,voice)['code']=='queue_full'
            second.send_json({'type':'cancel'})
            until(second,'cancelled')
        assert len(engine.requests)==1
    released(engine)
    with client.websocket_connect('/tts/live') as fresh:
        start(fresh,voice,text='Hello world!')
        fresh.send_json({'type':'finish'})
        until(fresh,'done')
    released(engine)


def test_idle_source_times_out_and_next_client_can_run(api):
    client,engine,_,voice,_=api
    with client.websocket_connect('/tts/live') as socket:
        start(socket,voice,input_timeout_s=1)
        assert until(socket,'error')['code']=='input_timeout'
    released(engine)


def test_foreign_browser_origin_is_rejected(api):
    client,engine,_,_,_=api
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect('/tts/live',headers={'origin':'https://unrelated.example'}):
            pytest.fail('Foreign origin accepted')
    assert not engine.admissions


def test_discovery_reports_live_protocol(api):
    client,*_=api
    capability=client.get('/studio/capabilities').json()['live_speech']
    assert capability['path']=='/tts/live' and capability['utterances_per_connection']==1
    assert capability['cloning_modes']['icl']=={'xvec_only':False}
    assert capability['models']==[LIVE_MODEL]
    assert capability['default_model']==LIVE_MODEL


@pytest.mark.parametrize('xvec_only', [False, True])
def test_live_rejects_06_before_admission_in_both_clone_modes(api,monkeypatch,xvec_only):
    client,engine,_,voice,_=api
    monkeypatch.setattr(engine,'admit',lambda: pytest.fail('Unsupported model entered the queue'))
    with client.websocket_connect('/tts/live') as socket:
        error=start(socket,voice,model='Qwen/Qwen3-TTS-12Hz-0.6B-Base',xvec_only=xvec_only)
        assert error['type']=='error' and error['code']=='invalid_request'
        assert LIVE_MODEL in error['message']
    assert not engine.requests and not engine.admissions


def test_live_defaults_to_supported_model_when_http_clone_default_is_06(api):
    client,engine,_,voice,_=api
    engine.workflow_models['clone']='Qwen/Qwen3-TTS-12Hz-0.6B-Base'
    with client.websocket_connect('/tts/live') as socket:
        assert start(socket,voice,text='Hello world!')['model']==LIVE_MODEL
        socket.send_json({'type':'finish'})
        until(socket,'done')
    assert engine.requests[-1].model==LIVE_MODEL
    assert engine.workflow_models['clone']=='Qwen/Qwen3-TTS-12Hz-0.6B-Base'
    released(engine)


def test_transcript_override_is_used_for_full_reference_cloning(api):
    client,engine,store,voice,_=api
    store.update(voice,{'transcript':''})
    with client.websocket_connect('/tts/live') as socket:
        assert start(socket,voice,ref_text='The corrected reference words.')['type']=='accepted'
        socket.send_json({'type':'text','text':'Hello world!'})
        socket.send_json({'type':'finish'})
        until(socket,'done')
    assert engine.requests[-1].ref_text=='The corrected reference words.'
    released(engine)


@pytest.mark.parametrize('options',[{'non_streaming_mode':True},{'mode':'design'},
                                    {'response_format':'wav'},{'input_type':'ssml'}])
def test_unsupported_semantics_are_not_silently_ignored(api,options):
    client,engine,_,voice,_=api
    with client.websocket_connect('/tts/live') as socket:
        assert start(socket,voice,**options)['type']=='error'
    assert not engine.admissions


def test_slow_audio_consumer_cancels_worker_and_releases_lease(api,monkeypatch):
    from fastapi import WebSocket
    from faster_qwen3_tts.standalone_ui import live_api
    async def stalled_send(self,content):
        await asyncio.sleep(1)
    monkeypatch.setattr(live_api,'SEND_TIMEOUT',.03)
    monkeypatch.setattr(WebSocket,'send_bytes',stalled_send)
    client,engine,_,voice,_=api
    with client.websocket_connect('/tts/live') as socket:
        start(socket,voice,text='Hello world! '*20)
        socket.send_json({'type':'finish'})
        while socket.receive()['type']!='websocket.close':
            pass
    released(engine)


def test_connection_deadline_releases_waiting_worker(api,monkeypatch):
    from faster_qwen3_tts.standalone_ui import live_api
    monkeypatch.setattr(live_api,'MAX_CONNECTION_SECONDS',.03)
    client,engine,_,voice,_=api
    with client.websocket_connect('/tts/live') as socket:
        start(socket,voice)
        while socket.receive()['type']!='websocket.close':
            pass
    released(engine)
