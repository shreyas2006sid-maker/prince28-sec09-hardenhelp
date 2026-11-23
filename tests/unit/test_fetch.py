from pathlib import Path

import pytest

from hardenhelp.ingest.fetch import (
    Downloader,
    Source,
    download_url,
    is_retryable_status,
    licence_is_approved,
    read_sources,
    retry_after_seconds,
    safe_filename,
)


def test_read_sources(tmp_path: Path) -> None:
    """Read source records and ignore comment lines."""
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
    """Reject CSV files with missing required columns."""
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text("url,source,title\n", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV must contain"):
        read_sources(csv_file)


def test_read_sources_skips_empty_urls(tmp_path: Path) -> None:
    """Skip records without a URL."""
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
    """Approve ComplianceAsCode records labelled BSD-3-Clause."""
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
    """Reject sources outside the approved source and licence combination."""
    source = Source(
        url="https://example.com/file",
        source=source_name,
        licence=licence,
        title="Blocked File",
    )

    assert licence_is_approved(source) is False


def test_download_url_preserves_original_url() -> None:
    """Keep the original source URL unchanged."""
    url = "https://github.com/example/project/blob/main/file.txt"

    assert download_url(url) == url


def test_safe_filename() -> None:
    """Generate a safe filename from a URL."""
    filename = safe_filename("https://example.com/files/test file.txt")

    assert filename.endswith("_test_file.txt")
    assert "/" not in filename
    assert "\\" not in filename


def test_safe_filename_is_unique_for_different_urls() -> None:
    """Generate different filenames for different URLs."""
    first = safe_filename("https://example.com/file.txt")
    second = safe_filename("https://another.com/file.txt")

    assert first != second


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
def test_retry_after_seconds(value: str | None, expected: float | None) -> None:
    """Parse numeric Retry-After values."""
    assert retry_after_seconds(value) == expected


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
    """Identify HTTP statuses that can be retried."""
    assert is_retryable_status(status) is expected


def test_downloader_rejects_negative_delay(tmp_path: Path) -> None:
    """Reject negative request delays."""
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
    """Reject concurrency outside the allowed range."""
    with pytest.raises(ValueError, match="between 1 and 4"):
        Downloader(
            output_dir=tmp_path / "raw",
            manifest_path=tmp_path / "manifest.jsonl",
            max_concurrency=concurrency,
        )


def test_downloader_rejects_invalid_attempts(tmp_path: Path) -> None:
    """Reject zero download attempts."""
    with pytest.raises(ValueError, match="at least 1"):
        Downloader(
            output_dir=tmp_path / "raw",
            manifest_path=tmp_path / "manifest.jsonl",
            max_attempts=0,
        )
