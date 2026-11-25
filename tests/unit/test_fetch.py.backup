from pathlib import Path

import httpx
import pytest

from hardenhelp.ingest.fetch import (
    Downloader,
    Source,
    download_url,
    is_retryable_status,
    licence_is_approved,
    looks_like_html,
    read_sources,
    retry_after_seconds,
    retry_delay,
    safe_filename,
    validate_content_range,
    validate_content_type,
)


def test_read_sources(tmp_path: Path) -> None:
    csv_file = tmp_path / "sources.csv"
    csv_file.write_text(
        "# Source inventory\n"
        "url,source,licence,title\n"
        "https://example.com/file.txt,Example,BSD-3-Clause,Example File\n",
        encoding="utf-8",
    )

    sources = read_sources(csv_file)

    assert len(sources) == 1
    assert sources[0] == Source(
        url="https://example.com/file.txt",
        source="Example",
        licence="BSD-3-Clause",
        title="Example File",
    )


def test_read_sources_missing_columns(tmp_path: Path) -> None:
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text("url,source,title\n", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV must contain"):
        read_sources(csv_file)


def test_read_sources_skips_empty_urls(tmp_path: Path) -> None:
    csv_file = tmp_path / "sources.csv"
    csv_file.write_text(
        "url,source,licence,title\n"
        ",Example,BSD-3-Clause,Empty URL\n"
        "https://example.com/file.txt,Example,BSD-3-Clause,Valid URL\n",
        encoding="utf-8",
    )

    sources = read_sources(csv_file)

    assert len(sources) == 1
    assert sources[0].title == "Valid URL"


def test_licence_is_approved() -> None:
    source = Source(
        url="https://example.com/file",
        source="ComplianceAsCode",
        licence="BSD-3-Clause",
        title="Approved File",
    )

    assert licence_is_approved(source) is True


@pytest.mark.parametrize(
    ("source_name", "licence"),
    [
        ("DISA", "BSD-3-Clause"),
        ("NIST", "Public Domain"),
        ("ComplianceAsCode", "MIT"),
        ("Ubuntu", "GPL-3.0"),
    ],
)
def test_licence_is_blocked(source_name: str, licence: str) -> None:
    source = Source(
        url="https://example.com/file",
        source=source_name,
        licence=licence,
        title="Blocked File",
    )

    assert licence_is_approved(source) is False


def test_download_url_converts_github_blob_url() -> None:
    url = "https://github.com/ComplianceAsCode/content/blob/main/linux_os/guide/example.yml"
    expected = (
        "https://raw.githubusercontent.com/ComplianceAsCode/content/main/linux_os/guide/example.yml"
    )

    assert download_url(url) == expected


def test_download_url_preserves_non_github_url() -> None:
    url = "https://example.com/files/example.yml"

    assert download_url(url) == url


def test_download_url_preserves_unsupported_github_url() -> None:
    url = "https://github.com/example/project/tree/main/file.txt"

    assert download_url(url) == url


def test_safe_filename() -> None:
    filename = safe_filename("https://example.com/files/test file.txt")

    assert filename.endswith("_test_file.txt")
    assert "/" not in filename
    assert "\\" not in filename


def test_safe_filename_is_unique_for_different_urls() -> None:
    first = safe_filename("https://example.com/file.txt")
    second = safe_filename("https://another.com/file.txt")

    assert first != second


def test_safe_filename_removes_unsafe_characters() -> None:
    result = safe_filename("https://example.com/../../Alpha Rule!")

    assert result.endswith("_Alpha_Rule_")
    assert "/" not in result
    assert "\\" not in result


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("10", 10.0),
        ("0", 0.0),
        ("-5", 0.0),
        (None, None),
        ("invalid", None),
    ],
)
def test_retry_after_seconds(
    value: str | None,
    expected: float | None,
) -> None:
    assert retry_after_seconds(value) == expected


def test_retry_delay_uses_exponential_backoff() -> None:
    assert retry_delay(1) >= 2
    assert retry_delay(1) < 3


def test_retry_delay_uses_retry_after_value() -> None:
    assert retry_delay(1, retry_after=10) == 10


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (200, False),
        (301, False),
        (400, False),
        (408, True),
        (425, True),
        (429, True),
        (500, True),
        (503, True),
        (599, True),
        (600, False),
    ],
)
def test_is_retryable_status(status: int, expected: bool) -> None:
    assert is_retryable_status(status) is expected


@pytest.mark.parametrize(
    "content_type",
    [
        "text/html",
        "text/html; charset=utf-8",
        "application/xhtml+xml",
    ],
)
def test_validate_content_type_rejects_html(content_type: str) -> None:
    with pytest.raises(ValueError):
        validate_content_type(content_type)


@pytest.mark.parametrize(
    "content_type",
    [
        "text/plain",
        "application/yaml",
        "application/octet-stream",
        "application/json",
    ],
)
def test_validate_content_type_accepts_non_html(content_type: str) -> None:
    validate_content_type(content_type)


def test_looks_like_html_detects_html() -> None:
    assert looks_like_html(b"<!DOCTYPE html><html>")


def test_looks_like_html_detects_html_with_leading_spaces() -> None:
    assert looks_like_html(b"   <html><body>Example</body></html>")


def test_looks_like_html_rejects_plain_text() -> None:
    assert not looks_like_html(b"Ubuntu security rule")


def test_looks_like_html_rejects_empty_content() -> None:
    assert not looks_like_html(b"")


def test_validate_content_range_accepts_valid_range() -> None:
    assert validate_content_range("bytes 100-199/500", 100) == 100


def test_validate_content_range_rejects_wrong_start() -> None:
    with pytest.raises(ValueError):
        validate_content_range("bytes 0-99/500", 100)


def test_validate_content_range_rejects_invalid_format() -> None:
    with pytest.raises(ValueError):
        validate_content_range("invalid-range", 100)


def test_validate_content_range_rejects_end_before_start() -> None:
    with pytest.raises(ValueError):
        validate_content_range("bytes 100-99/500", 100)


def test_validate_content_range_rejects_end_beyond_total() -> None:
    with pytest.raises(ValueError):
        validate_content_range("bytes 100-500/500", 100)


def test_validate_content_range_rejects_negative_offset() -> None:
    with pytest.raises(ValueError):
        validate_content_range("bytes 0-99/500", -1)


@pytest.mark.asyncio
async def test_download_rejects_partial_response_without_resume(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = Source(
        url="https://example.com/file.yml",
        source="ComplianceAsCode",
        licence="BSD-3-Clause",
        title="Example",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            206,
            headers={
                "Content-Type": "text/plain",
                "Content-Range": "bytes 0-2/3",
            },
            content=b"abc",
        )

    async def allow_robots(url: str) -> bool:
        return True

    async with Downloader(
        tmp_path / "raw",
        tmp_path / "manifest.jsonl",
        delay=0,
        max_attempts=1,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()
        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        monkeypatch.setattr(downloader, "_robots_allowed", allow_robots)

        result = await downloader.download(source)

    assert result["status"] == "failed"
    assert "without a resume request" in result["error"]


@pytest.mark.asyncio
async def test_download_rejects_incomplete_resumed_response(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = Source(
        url="https://example.com/file.yml",
        source="ComplianceAsCode",
        licence="BSD-3-Clause",
        title="Example",
    )

    class IncompleteStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b"cd"

        async def aclose(self) -> None:
            pass

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Range"] == "bytes=2-"

        return httpx.Response(
            206,
            headers={
                "Content-Type": "text/plain",
                "Content-Range": "bytes 2-4/5",
            },
            stream=IncompleteStream(),
        )

    async def allow_robots(url: str) -> bool:
        return True

    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    destination = output_dir / safe_filename(source.url)
    part_file = destination.with_name(destination.name + ".part")
    part_file.write_bytes(b"ab")

    async with Downloader(
        output_dir,
        tmp_path / "manifest.jsonl",
        delay=0,
        max_attempts=1,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()
        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        monkeypatch.setattr(downloader, "_robots_allowed", allow_robots)

        result = await downloader.download(source)

    assert result["status"] == "failed"
    assert "byte count does not match" in result["error"]
    assert part_file.read_bytes() == b"ab"
    assert not destination.exists()


@pytest.mark.asyncio
async def test_download_rejects_html_response(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = Source(
        url="https://example.com/file.yml",
        source="ComplianceAsCode",
        licence="BSD-3-Clause",
        title="Example",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"Content-Type": "text/html"},
            content=b"<html>Example error page</html>",
        )

    async def allow_robots(url: str) -> bool:
        return True

    async with Downloader(
        tmp_path / "raw",
        tmp_path / "manifest.jsonl",
        delay=0,
        max_attempts=1,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()
        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        monkeypatch.setattr(downloader, "_robots_allowed", allow_robots)

        result = await downloader.download(source)

    assert result["status"] == "failed"
    assert "HTML" in result["error"]
    assert not list((tmp_path / "raw").glob("*.part"))


def test_downloader_rejects_negative_delay(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="delay cannot be negative"):
        Downloader(
            output_dir=tmp_path / "raw",
            manifest_path=tmp_path / "manifest.jsonl",
            delay=-1,
        )


@pytest.mark.parametrize("concurrency", [0, 5, 10])
def test_downloader_rejects_invalid_concurrency(
    tmp_path: Path,
    concurrency: int,
) -> None:
    with pytest.raises(ValueError, match="between 1 and 4"):
        Downloader(
            output_dir=tmp_path / "raw",
            manifest_path=tmp_path / "manifest.jsonl",
            max_concurrency=concurrency,
        )


def test_downloader_rejects_invalid_attempts(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="at least 1"):
        Downloader(
            output_dir=tmp_path / "raw",
            manifest_path=tmp_path / "manifest.jsonl",
            max_attempts=0,
        )


@pytest.mark.asyncio
async def test_download_preserves_partial_file_when_restart_response_is_invalid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = Source(
        url="https://example.com/file.yml",
        source="ComplianceAsCode",
        licence="BSD-3-Clause",
        title="Example",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"Content-Type": "text/html"},
            content=b"<html>Invalid response</html>",
        )

    async def allow_robots(url: str) -> bool:
        return True

    output_dir = tmp_path / "raw"
    output_dir.mkdir()

    destination = output_dir / safe_filename(source.url)
    part_file = destination.with_name(destination.name + ".part")
    part_file.write_bytes(b"original partial data")

    async with Downloader(
        output_dir,
        tmp_path / "manifest.jsonl",
        delay=0,
        max_attempts=1,
    ) as downloader:
        assert downloader.client is not None
        await downloader.client.aclose()
        downloader.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        monkeypatch.setattr(downloader, "_robots_allowed", allow_robots)

        result = await downloader.download(source)

    assert result["status"] == "failed"
    assert "HTML" in result["error"]
    assert part_file.read_bytes() == b"original partial data"
    assert not destination.exists()
    assert not list(output_dir.glob("*.restart"))
