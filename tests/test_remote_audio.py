from __future__ import annotations

import asyncio

import httpx
import pytest

from faster_qwen3_tts.standalone_ui.remote_audio import RemoteAudioError, RemoteAudioFetcher


def test_remote_audio_download_is_bounded() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=b"12345", request=request))
    fetcher = RemoteAudioFetcher(
        max_bytes=4,
        allowed_hosts=["audio.example"],
        transport=transport,
        resolver=lambda host, port: ["8.8.8.8"],
    )
    with pytest.raises(RemoteAudioError, match="limit"):
        asyncio.run(fetcher.fetch("https://audio.example/reference.wav"))


def test_remote_audio_redirect_destination_is_revalidated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            302,
            headers={"location": "http://169.254.169.254/metadata.wav"},
            request=request,
        )

    fetcher = RemoteAudioFetcher(
        max_bytes=1024,
        allowed_hosts=["*"],
        transport=httpx.MockTransport(handler),
        resolver=lambda host, port: [host if host[0].isdigit() else "8.8.8.8"],
    )
    with pytest.raises(RemoteAudioError, match="link-local"):
        asyncio.run(fetcher.fetch("https://audio.example/reference.wav"))


def test_dns_result_is_pinned_while_tls_and_host_retain_the_original_name():
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, content=b'valid reference', request=request)
    fetcher = RemoteAudioFetcher(max_bytes=100, allowed_hosts=['audio.example'],
        transport=httpx.MockTransport(handler), resolver=lambda host, port: ['8.8.8.8'])
    result = asyncio.run(fetcher.fetch('https://audio.example/reference.wav'))
    assert result.payload == b'valid reference'
    assert requests[0].url.host == '8.8.8.8'
    assert requests[0].headers['host'] == 'audio.example'
    assert requests[0].extensions['sni_hostname'] == 'audio.example'
    assert result.filename == 'reference.wav'


def test_localhost_capability_links_work_with_dual_stack_dns():
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, content=b'local audio', request=request)
    fetcher = RemoteAudioFetcher(max_bytes=100, allowed_hosts=['localhost:7860'],
        transport=httpx.MockTransport(handler), resolver=lambda host, port: ['::1', '127.0.0.1'])
    downloaded = asyncio.run(fetcher.fetch('http://localhost:7860/tts/artifacts/token'))
    assert downloaded.payload == b'local audio'
    assert requests[0].url.host == '::1' and requests[0].headers['host'] == 'localhost:7860'


def test_ipv6_metadata_address_is_rejected_even_though_it_is_private():
    fetcher = RemoteAudioFetcher(max_bytes=100, allowed_hosts=['*'],
        transport=httpx.MockTransport(lambda request: pytest.fail('Unexpected metadata access')),
        resolver=lambda host, port: ['fd00:ec2::254'])
    with pytest.raises(RemoteAudioError, match='link-local, reserved'):
        asyncio.run(fetcher.fetch('http://[fd00:ec2::254]/latest/meta-data/'))


def test_total_download_deadline_bounds_slow_trickle():
    class Slow(httpx.AsyncByteStream):
        async def __aiter__(self):
            for _ in range(20):
                await asyncio.sleep(.02)
                yield b'a'
    fetcher = RemoteAudioFetcher(max_bytes=1000, allowed_hosts=['audio.example'], timeout_seconds=.05,
        transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=Slow())),
        resolver=lambda host, port: ['8.8.8.8'])
    with pytest.raises(RemoteAudioError, match='total time'):
        asyncio.run(fetcher.fetch('http://audio.example/reference.wav'))


@pytest.mark.parametrize('location', ['file:///etc/passwd', 'https://user:password@audio.example/a.wav', 'http://bad.example/a.wav'])
def test_invalid_reference_authorities_are_rejected_before_network(location):
    fetcher = RemoteAudioFetcher(max_bytes=1000, allowed_hosts=['audio.example'],
        transport=httpx.MockTransport(lambda request: pytest.fail('Unexpected network access')))
    with pytest.raises(RemoteAudioError):
        asyncio.run(fetcher.fetch(location))
