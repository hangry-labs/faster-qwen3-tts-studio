"""Stream an async text source to the native speech API and save its PCM as WAV.

Install the client dependency with: python -m pip install websockets
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import wave

from websockets.asyncio.client import connect


async def speak(fragments, *, voice, output='speech.wav', url='ws://localhost:7860/tts/live',
                model='Qwen/Qwen3-TTS-12Hz-1.7B-Base', xvec_only=False, seed=4210):
    """fragments is an async iterable of text deltas, such as an LLM response."""
    destination = Path(output)
    temporary = None
    try:
        async with connect(url, max_size=1024*1024) as socket:
            await socket.send(json.dumps({'type':'start','voice':voice,'model':model,
                                          'xvec_only':xvec_only,'seed':seed}))
            accepted = json.loads(await socket.recv())
            if accepted.get('type') != 'accepted':
                raise RuntimeError(accepted.get('message','Speech session was not accepted.'))
            with tempfile.NamedTemporaryFile(prefix='.live-',suffix='.wav',dir=destination.parent,delete=False) as file:
                temporary = Path(file.name)
            result = None
            with wave.open(str(temporary),'wb') as sink:
                sink.setnchannels(accepted['channels'])
                sink.setsampwidth(2)
                sink.setframerate(accepted['sample_rate'])

                async def send_text():
                    async for text in fragments:
                        await socket.send(json.dumps({'type':'text','text':text},ensure_ascii=False))
                    await socket.send(json.dumps({'type':'finish'}))

                async def receive_audio():
                    nonlocal result
                    async for message in socket:
                        if isinstance(message,bytes):
                            if len(message)%2:
                                raise RuntimeError('Received an incomplete PCM sample.')
                            sink.writeframesraw(message)
                        else:
                            event = json.loads(message)
                            if event['type'] in {'error','cancelled'}:
                                raise RuntimeError(event.get('message','Speech was cancelled.'))
                            if event['type']=='done':
                                result = event
                                return
                    raise RuntimeError('Speech connection ended without a done event.')

                async with asyncio.TaskGroup() as tasks:
                    tasks.create_task(send_text())
                    tasks.create_task(receive_audio())
            os.replace(temporary,destination)
            temporary = None
            return result
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice',required=True,help='Saved voice ID or unique name')
    parser.add_argument('--url',default='ws://localhost:7860/tts/live')
    parser.add_argument('--model',default='Qwen/Qwen3-TTS-12Hz-1.7B-Base')
    parser.add_argument('--speaker-only',action='store_true')
    parser.add_argument('--seed',type=int,default=4210)
    parser.add_argument('--output',default='speech.wav')
    parser.add_argument('--text',help='Send one complete text; otherwise read fragments from stdin until EOF')
    args = parser.parse_args()

    async def fragments():
        if args.text is not None:
            yield args.text
        else:
            while line := await asyncio.to_thread(sys.stdin.readline):
                yield line

    await speak(fragments(),voice=args.voice,output=args.output,url=args.url,model=args.model,
                xvec_only=args.speaker_only,seed=args.seed)
    print('Saved '+str(Path(args.output).resolve()))


if __name__=='__main__':
    asyncio.run(main())
