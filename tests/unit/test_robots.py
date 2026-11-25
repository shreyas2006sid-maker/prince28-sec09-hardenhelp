"""Tests for robots.txt handling in the HardenHelp downloader."""

from pathlib import Path

import httpx
import pytest

from hardenhelp.ingest.fetch import Downloader


@pytest.mark.asyncio
async def test_robots_allows_when_file_returns_404(tmp_path: Path) -> None:
    """A missing robots.txt means there are no published crawler rules."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/robots.txt"
        return httpx.Response(404)

    async with Downloader(
        tmp_path / "raw",
        tmp_path / "manifest.jsonl",
        delay=0,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()

        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

        assert await downloader._robots_allowed("https://example.com/file.yml") is True

        await downloader.client.aclose()
        downloader.client = None


@pytest.mark.asyncio
async def test_robots_blocks_disallowed_path(tmp_path: Path) -> None:
    """Protego must block paths disallowed for our User-Agent."""

    robots_content = """
User-agent: *
Disallow: /private/
Allow: /private/public.yml
"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=robots_content)

    async with Downloader(
        tmp_path / "raw",
        tmp_path / "manifest.jsonl",
        delay=0,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()

        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

        assert await downloader._robots_allowed("https://example.com/private/secret.yml") is False

        assert await downloader._robots_allowed("https://example.com/public/file.yml") is True

        assert await downloader.client.aclose() is None
        downloader.client = None


@pytest.mark.asyncio
async def test_robots_allows_explicitly_allowed_path(tmp_path: Path) -> None:
    """An explicitly allowed path can be crawled."""

    robots_content = """
User-agent: *
Disallow: /
Allow: /approved/
"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=robots_content)

    async with Downloader(
        tmp_path / "raw",
        tmp_path / "manifest.jsonl",
        delay=0,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()

        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

        assert await downloader._robots_allowed("https://example.com/approved/file.yml") is True

        assert await downloader._robots_allowed("https://example.com/blocked/file.yml") is False

        await downloader.client.aclose()
        downloader.client = None


@pytest.mark.parametrize("status_code", [403, 429, 500, 503])
@pytest.mark.asyncio
async def test_robots_fails_closed_for_unexpected_status(
    tmp_path: Path,
    status_code: int,
) -> None:
    """Unexpected robots.txt responses must block downloading."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    async with Downloader(
        tmp_path / "raw",
        tmp_path / "manifest.jsonl",
        delay=0,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()

        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

        assert await downloader._robots_allowed("https://example.com/file.yml") is False

        await downloader.client.aclose()
        downloader.client = None


@pytest.mark.asyncio
async def test_robots_fails_closed_on_network_error(tmp_path: Path) -> None:
    """Network errors while checking robots.txt must block downloading."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Simulated connection failure")

    async with Downloader(
        tmp_path / "raw",
        tmp_path / "manifest.jsonl",
        delay=0,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()

        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

        assert await downloader._robots_allowed("https://example.com/file.yml") is False

        await downloader.client.aclose()
        downloader.client = None
