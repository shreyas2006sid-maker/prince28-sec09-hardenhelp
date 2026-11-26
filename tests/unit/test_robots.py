"""Tests for robots.txt handling in the HardenHelp downloader."""

import httpx
import pytest

from hardenhelp.ingest.fetch import Robots


@pytest.mark.asyncio
async def test_robots_allows_when_file_returns_404() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/robots.txt"
        return httpx.Response(404)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        robots = Robots(client)
        allowed, _ = await robots.check("https://example.com/file.yml")

    assert allowed is True


@pytest.mark.asyncio
async def test_robots_blocks_disallowed_path() -> None:
    robots_content = """
User-agent: *
Disallow: /private/
Allow: /private/public.yml
"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=robots_content)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        robots = Robots(client)

        blocked, _ = await robots.check("https://example.com/private/secret.yml")
        allowed, _ = await robots.check("https://example.com/public/file.yml")

    assert blocked is False
    assert allowed is True


@pytest.mark.asyncio
async def test_robots_allows_explicitly_allowed_path() -> None:
    robots_content = """
User-agent: *
Disallow: /
Allow: /approved/
"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=robots_content)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        robots = Robots(client)

        allowed, _ = await robots.check("https://example.com/approved/file.yml")
        blocked, _ = await robots.check("https://example.com/blocked/file.yml")

    assert allowed is True
    assert blocked is False


@pytest.mark.parametrize("status_code", [429, 500, 503])
@pytest.mark.asyncio
async def test_robots_fails_closed_for_server_errors(
    status_code: int,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        robots = Robots(client)
        allowed, _ = await robots.check("https://example.com/file.yml")

    assert allowed is False


@pytest.mark.parametrize("status_code", [403, 404])
@pytest.mark.asyncio
async def test_robots_allows_when_file_is_unavailable(
    status_code: int,
) -> None:
    """RFC 9309 treats 4xx robots.txt responses as unavailable."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        robots = Robots(client)
        allowed, _ = await robots.check("https://example.com/file.yml")

    assert allowed is True


@pytest.mark.asyncio
async def test_robots_fails_closed_on_network_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Simulated connection failure")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        robots = Robots(client)
        allowed, _ = await robots.check("https://example.com/file.yml")

    assert allowed is False
