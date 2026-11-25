import pytest

from hardenhelp.ingest import repo
from hardenhelp.ingest.fetch import Source

COMMIT_SHA = "a" * 40


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeClient:
    def __init__(self, responses: list[dict]) -> None:
        self.responses = iter(responses)
        self.requested_urls: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def get(self, url: str) -> FakeResponse:
        self.requested_urls.append(url)
        return FakeResponse(next(self.responses))


def install_fake_client(monkeypatch, responses: list[dict]) -> FakeClient:
    client = FakeClient(responses)

    monkeypatch.setattr(
        repo.httpx,
        "Client",
        lambda **kwargs: client,
    )

    return client


def valid_repository_response() -> dict:
    return {
        "license": {
            "spdx_id": "BSD-3-Clause",
        }
    }


def valid_commit_response() -> dict:
    return {
        "sha": COMMIT_SHA,
    }


def test_discover_repository_sources(monkeypatch) -> None:
    client = install_fake_client(
        monkeypatch,
        [
            valid_repository_response(),
            valid_commit_response(),
            {
                "truncated": False,
                "tree": [
                    {
                        "type": "blob",
                        "path": "linux_os/guide/rule.yml",
                    },
                    {
                        "type": "blob",
                        "path": "linux_os/guide/metadata.json",
                    },
                    {
                        "type": "blob",
                        "path": "linux_os/guide/readme.txt",
                    },
                    {
                        "type": "tree",
                        "path": "linux_os/guide/subdirectory",
                    },
                    {
                        "type": "blob",
                        "path": "other/rule.yml",
                    },
                ],
            },
        ],
    )

    commit_sha, sources = repo.discover_repository_sources(
        path_prefixes=["linux_os/guide"],
    )

    assert commit_sha == COMMIT_SHA
    assert len(sources) == 2

    assert sources[0] == Source(
        url=(
            "https://raw.githubusercontent.com/"
            f"ComplianceAsCode/content/{COMMIT_SHA}/"
            "linux_os/guide/metadata.json"
        ),
        source="ComplianceAsCode",
        licence="BSD-3-Clause",
        title="linux_os/guide/metadata.json",
    )

    assert sources[1].title == "linux_os/guide/rule.yml"
    assert all(source.url.find(COMMIT_SHA) != -1 for source in sources)
    assert len(client.requested_urls) == 3


def test_discover_repository_sources_uses_extension_filter(
    monkeypatch,
) -> None:
    install_fake_client(
        monkeypatch,
        [
            valid_repository_response(),
            valid_commit_response(),
            {
                "truncated": False,
                "tree": [
                    {"type": "blob", "path": "rules/one.yml"},
                    {"type": "blob", "path": "rules/two.xml"},
                    {"type": "blob", "path": "rules/three.json"},
                ],
            },
        ],
    )

    _, sources = repo.discover_repository_sources(
        extensions={".xml"},
    )

    assert [source.title for source in sources] == ["rules/two.xml"]


def test_discover_repository_sources_rejects_other_repository() -> None:
    with pytest.raises(ValueError, match="restricted"):
        repo.discover_repository_sources(
            owner="another-owner",
            repository="another-repository",
        )


def test_discover_repository_sources_rejects_unapproved_licence(
    monkeypatch,
) -> None:
    install_fake_client(
        monkeypatch,
        [
            {
                "license": {
                    "spdx_id": "MIT",
                }
            },
        ],
    )

    with pytest.raises(ValueError, match="licence is not approved"):
        repo.discover_repository_sources()


def test_discover_repository_sources_rejects_invalid_commit_sha(
    monkeypatch,
) -> None:
    install_fake_client(
        monkeypatch,
        [
            valid_repository_response(),
            {"sha": "not-a-valid-commit"},
        ],
    )

    with pytest.raises(ValueError, match="invalid commit SHA"):
        repo.discover_repository_sources()


def test_discover_repository_sources_rejects_truncated_tree(
    monkeypatch,
) -> None:
    install_fake_client(
        monkeypatch,
        [
            valid_repository_response(),
            valid_commit_response(),
            {
                "truncated": True,
                "tree": [],
            },
        ],
    )

    with pytest.raises(ValueError, match="truncated"):
        repo.discover_repository_sources()


def test_discover_repository_sources_rejects_empty_ref() -> None:
    with pytest.raises(ValueError, match="ref cannot be empty"):
        repo.discover_repository_sources(ref="   ")


def test_discover_repository_sources_rejects_invalid_extension() -> None:
    with pytest.raises(ValueError, match="Extensions must be lowercase"):
        repo.discover_repository_sources(extensions={"yml"})


def test_discover_repository_sources_rejects_uppercase_extension() -> None:
    with pytest.raises(ValueError, match="Extensions must be lowercase"):
        repo.discover_repository_sources(extensions={".YML"})
