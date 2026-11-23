"""Polite, resumable downloader for approved HardenHelp sources."""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import random
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx

USER_AGENT = (
    "HardenHelpBot/0.1 (+https://github.com/shreyas2006sid-maker/prince28-sec09-hardenhelp)"
)
TIMEOUT = httpx.Timeout(30.0, connect=10.0)
MAX_CONCURRENCY = 4


@dataclass(frozen=True)
class Source:
    """One source from the CSV inventory."""

    url: str
    source: str
    licence: str
    title: str


def read_sources(csv_path: Path) -> list[Source]:
    """Read source records while ignoring comment lines."""
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as file:
        lines = (line for line in file if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(lines)

        required = {"url", "source", "licence", "title"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV must contain url, source, licence, and title columns.")

        sources = []
        for row in reader:
            if not row.get("url", "").strip():
                continue

            sources.append(
                Source(
                    url=row["url"].strip(),
                    source=row["source"].strip(),
                    licence=row["licence"].strip(),
                    title=row["title"].strip(),
                )
            )

    return sources


def licence_is_approved(source: Source) -> bool:
    """Allow only explicitly identified BSD-3-Clause ComplianceAsCode records."""
    return (
        source.source.casefold() == "complianceascode"
        and "bsd-3-clause" in source.licence.casefold()
    )


def download_url(url: str) -> str:
    """Return the original source URL without modifying it."""
    return url


def safe_filename(url: str) -> str:
    """Generate a filesystem-safe, URL-specific filename."""
    parsed = urlsplit(url)
    name = Path(parsed.path).name or "download"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return f"{digest}_{name}"


def retry_after_seconds(value: str | None) -> float | None:
    """Parse a Retry-After header as seconds or an HTTP date."""
    if not value:
        return None

    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_time = parsedate_to_datetime(value)
            if retry_time.tzinfo is None:
                retry_time = retry_time.replace(tzinfo=UTC)

            return max(
                0.0,
                (retry_time - datetime.now(UTC)).total_seconds(),
            )
        except (TypeError, ValueError, OverflowError):
            return None


def retry_delay(attempt: int, retry_after: float | None = None) -> float:
    """Calculate exponential backoff with jitter."""
    if retry_after is not None:
        return retry_after

    return min(60.0, 2**attempt) + random.uniform(0.0, 1.0)


def is_retryable_status(status: int) -> bool:
    """Identify HTTP statuses that can be retried."""
    return status in {408, 425, 429} or 500 <= status <= 599


class Downloader:
    """Download approved files with robots checks and resumable partial files."""

    def __init__(
        self,
        output_dir: Path,
        manifest_path: Path,
        delay: float = 1.0,
        max_concurrency: int = 4,
        max_attempts: int = 4,
    ) -> None:
        if delay < 0:
            raise ValueError("delay cannot be negative")
        if not 1 <= max_concurrency <= MAX_CONCURRENCY:
            raise ValueError("max_concurrency must be between 1 and 4")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self.output_dir = Path(output_dir)
        self.manifest_path = Path(manifest_path)
        self.delay = delay
        self.max_attempts = max_attempts

        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.manifest_lock = asyncio.Lock()

        self.client: httpx.AsyncClient | None = None
        self.robots_cache: dict[str, RobotFileParser | None] = {}
        self.robots_locks: dict[str, asyncio.Lock] = {}
        self.host_locks: dict[str, asyncio.Lock] = {}
        self.last_request: dict[str, float] = {}

        self.completed: dict[str, str] = {}
        self.counts = {
            "downloaded": 0,
            "skipped": 0,
            "blocked": 0,
            "failed": 0,
        }

        self._load_manifest()

    async def __aenter__(self) -> Downloader:
        """Create output directories and open the HTTP client."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

        self.client = httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        """Close the HTTP client."""
        if self.client is not None:
            await self.client.aclose()

    def _load_manifest(self) -> None:
        """Load previously completed downloads."""
        if not self.manifest_path.exists():
            return

        with self.manifest_path.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    record = json.loads(line)

                    if record.get("status") != "downloaded":
                        continue

                    url = record.get("url")
                    path = record.get("path")

                    if url and path and Path(path).is_file():
                        self.completed[url] = path

                except (json.JSONDecodeError, OSError):
                    continue

    async def _robots_allowed(self, url: str) -> bool:
        """Check robots.txt before requesting a source file."""
        parsed = urlsplit(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urlunsplit((parsed.scheme, parsed.netloc, "/robots.txt", "", ""))

        lock = self.robots_locks.setdefault(origin, asyncio.Lock())

        async with lock:
            if origin not in self.robots_cache:
                parser = None

                try:
                    assert self.client is not None
                    response = await self.client.get(robots_url)

                    if response.status_code == 200:
                        parser = RobotFileParser()
                        parser.set_url(robots_url)
                        parser.parse(response.text.splitlines())

                except httpx.HTTPError:
                    parser = None

                self.robots_cache[origin] = parser

            parser = self.robots_cache[origin]

        if parser is None:
            return False

        return parser.can_fetch(USER_AGENT, url)

    async def _wait_for_host(self, host: str) -> None:
        """Enforce a minimum delay between requests to the same host."""
        lock = self.host_locks.setdefault(host, asyncio.Lock())

        async with lock:
            previous = self.last_request.get(host, 0.0)
            elapsed = time.monotonic() - previous
            remaining = self.delay - elapsed

            if remaining > 0:
                await asyncio.sleep(remaining)

            self.last_request[host] = time.monotonic()

    async def _write_manifest(self, record: dict) -> None:
        """Append a manifest record safely."""
        async with self.manifest_lock:
            with self.manifest_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record) + "\n")

    async def download(self, source: Source) -> dict:
        """Download one approved source and record its result."""
        url = source.url

        if not licence_is_approved(source):
            self.counts["blocked"] += 1
            return {
                "url": url,
                "status": "blocked",
                "error": "Redistribution licence has not been approved.",
            }

        if url in self.completed and Path(self.completed[url]).is_file():
            self.counts["skipped"] += 1
            return {"url": url, "status": "skipped"}

        fetch_url = download_url(url)

        if not await self._robots_allowed(fetch_url):
            self.counts["blocked"] += 1
            return {
                "url": url,
                "status": "blocked",
                "error": "Robots policy unavailable or downloading disallowed.",
            }

        destination = self.output_dir / safe_filename(url)
        part_file = destination.with_name(destination.name + ".part")
        host = urlsplit(fetch_url).netloc

        try:
            async with self.semaphore:
                for attempt in range(self.max_attempts):
                    await self._wait_for_host(host)

                    try:
                        assert self.client is not None

                        offset = part_file.stat().st_size if part_file.exists() else 0
                        headers = {}

                        if offset:
                            headers["Range"] = f"bytes={offset}-"

                        async with self.client.stream(
                            "GET",
                            fetch_url,
                            headers=headers,
                        ) as response:
                            if (
                                is_retryable_status(response.status_code)
                                and attempt + 1 < self.max_attempts
                            ):
                                wait = retry_delay(
                                    attempt,
                                    retry_after_seconds(response.headers.get("Retry-After")),
                                )
                                await asyncio.sleep(wait)
                                continue

                            response.raise_for_status()

                            if offset and response.status_code == 206:
                                content_range = response.headers.get("Content-Range", "")
                                if not content_range.startswith(f"bytes {offset}-"):
                                    raise ValueError("Server returned an unexpected partial range.")
                                mode = "ab"
                            else:
                                mode = "wb"
                                offset = 0

                            with part_file.open(mode) as file:
                                async for chunk in response.aiter_bytes():
                                    file.write(chunk)

                        part_file.replace(destination)

                        result = {
                            "url": url,
                            "download_url": fetch_url,
                            "path": str(destination),
                            "source": source.source,
                            "licence": source.licence,
                            "title": source.title,
                            "status": "downloaded",
                            "downloaded_at": datetime.now(UTC).isoformat(),
                        }

                        await self._write_manifest(result)
                        self.completed[url] = str(destination)
                        self.counts["downloaded"] += 1
                        return result

                    except httpx.TransportError:
                        if attempt + 1 >= self.max_attempts:
                            raise
                        await asyncio.sleep(retry_delay(attempt))

            raise RuntimeError("Download attempts exhausted.")

        except asyncio.CancelledError:
            # Keep the .part file so a later run can resume it.
            raise
        except Exception as error:
            self.counts["failed"] += 1
            return {
                "url": url,
                "status": "failed",
                "error": str(error),
            }

    async def download_many(
        self,
        sources: list[Source],
        on_result: Callable[[dict], None] | None = None,
    ) -> list[dict]:
        """Download multiple sources and optionally report each result."""

        async def process(source: Source) -> dict:
            result = await self.download(source)

            if on_result is not None:
                on_result(result)

            return result

        return await asyncio.gather(*(process(source) for source in sources))


async def fetch_all(
    sources: list[Source],
    root: Path,
    max_concurrency: int = 4,
    per_host_delay: float = 1.0,
    max_attempts: int = 4,
    on_result: Callable[[dict], None] | None = None,
) -> dict[str, int]:
    """Download approved sources into data/raw and return summary counts."""
    output_dir = Path(root) / "data" / "raw"
    manifest_path = output_dir / "manifest.jsonl"

    async with Downloader(
        output_dir=output_dir,
        manifest_path=manifest_path,
        delay=per_host_delay,
        max_concurrency=max_concurrency,
        max_attempts=max_attempts,
    ) as downloader:
        await downloader.download_many(sources, on_result)

        return downloader.counts.copy()
