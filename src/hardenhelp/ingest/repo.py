"""Discover approved files from the ComplianceAsCode GitHub repository."""

from __future__ import annotations

import os
from pathlib import PurePosixPath
from urllib.parse import quote

import httpx

from hardenhelp.ingest.fetch import USER_AGENT, Source

GITHUB_API = "https://api.github.com"
ALLOWED_OWNER = "ComplianceAsCode"
ALLOWED_REPOSITORY = "content"
APPROVED_LICENCE = "BSD-3-Clause"

DEFAULT_EXTENSIONS = {
    ".yml",
    ".yaml",
    ".xml",
    ".json",
    ".var",
}


def _headers() -> dict[str, str]:
    """Build GitHub API headers, optionally using a personal access token."""

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def _api_get(client: httpx.Client, url: str) -> dict:
    """Request one GitHub API resource and validate its response."""

    response = client.get(url)
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, dict):
        raise ValueError("GitHub API returned an unexpected response.")

    return payload


def _validate_repository(owner: str, repository: str) -> None:
    """Restrict collection to the approved ComplianceAsCode repository."""

    if (
        owner.casefold() != ALLOWED_OWNER.casefold()
        or repository.casefold() != ALLOWED_REPOSITORY.casefold()
    ):
        raise ValueError("Repository collection is restricted to ComplianceAsCode/content.")


def discover_repository_sources(
    owner: str = ALLOWED_OWNER,
    repository: str = ALLOWED_REPOSITORY,
    ref: str = "main",
    path_prefixes: list[str] | None = None,
    extensions: set[str] | None = None,
) -> tuple[str, list[Source]]:
    """Resolve a repository ref and discover approved files at its commit.

    Returns the resolved commit SHA and a list of downloader-compatible
    Source records. The GitHub repository licence must be BSD-3-Clause.
    """

    _validate_repository(owner, repository)

    if not ref.strip():
        raise ValueError("Repository ref cannot be empty.")

    requested_extensions = extensions if extensions is not None else DEFAULT_EXTENSIONS

    if any(
        not isinstance(extension, str)
        or not extension.startswith(".")
        or extension != extension.casefold()
        for extension in requested_extensions
    ):
        raise ValueError("Extensions must be lowercase and start with a dot.")

    selected_extensions = set(requested_extensions)

    prefixes = [
        prefix.strip("/").strip() for prefix in (path_prefixes or []) if prefix.strip("/").strip()
    ]

    base_url = f"{GITHUB_API}/repos/{owner}/{repository}"

    with httpx.Client(
        headers=_headers(),
        timeout=httpx.Timeout(30.0, connect=10.0),
        follow_redirects=True,
    ) as client:
        repository_data = _api_get(client, base_url)

        licence_data = repository_data.get("license") or {}
        spdx_id = licence_data.get("spdx_id")

        if spdx_id != APPROVED_LICENCE:
            raise ValueError(
                "Repository licence is not approved: "
                f"expected {APPROVED_LICENCE}, received {spdx_id!r}."
            )

        commit_data = _api_get(
            client,
            f"{base_url}/commits/{quote(ref, safe='')}",
        )

        commit_sha = commit_data.get("sha")

        if (
            not isinstance(commit_sha, str)
            or len(commit_sha) != 40
            or any(character not in "0123456789abcdef" for character in commit_sha.casefold())
        ):
            raise ValueError("GitHub API returned an invalid commit SHA.")

        tree_data = _api_get(
            client,
            f"{base_url}/git/trees/{commit_sha}?recursive=1",
        )

    if tree_data.get("truncated"):
        raise ValueError(
            "GitHub returned a truncated repository tree. "
            "Use a narrower path filter before collecting."
        )

    entries = tree_data.get("tree")

    if not isinstance(entries, list):
        raise ValueError("GitHub API did not return a valid repository tree.")

    sources: list[Source] = []

    for entry in entries:
        if not isinstance(entry, dict) or entry.get("type") != "blob":
            continue

        file_path = entry.get("path")

        if not isinstance(file_path, str):
            continue

        path = PurePosixPath(file_path)

        if path.suffix.casefold() not in selected_extensions:
            continue

        if prefixes and not any(
            file_path == prefix or file_path.startswith(prefix + "/") for prefix in prefixes
        ):
            continue

        encoded_path = quote(file_path, safe="/")

        raw_url = (
            f"https://raw.githubusercontent.com/{owner}/{repository}/{commit_sha}/{encoded_path}"
        )

        sources.append(
            Source(
                url=raw_url,
                source="ComplianceAsCode",
                licence=APPROVED_LICENCE,
                title=file_path,
            )
        )

    sources.sort(key=lambda source: source.title.casefold())

    return commit_sha, sources
