from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request

from hardenhelp.api.deps import check_db
from hardenhelp.config import Settings


def test_health_is_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "hardenhelp",
        "env": "ci",
        "version": "dev",
    }


def test_health_reports_configured_commit(client: TestClient, settings: Settings) -> None:
    settings.git_sha = "abc123"

    response = client.get("/health")

    assert response.json()["version"] == "abc123"


def test_ready_when_database_is_available(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["checks"]["database"] is True


def test_ready_is_503_when_database_is_unavailable(
    client: TestClient,
) -> None:
    client.app.dependency_overrides[check_db] = lambda: False

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"database": False},
    }


@pytest.mark.asyncio
async def test_check_db_returns_true_when_database_is_reachable() -> None:
    class Connection:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def execute(self, query: object) -> None:
            assert str(query) == "SELECT 1"

    class Engine:
        def connect(self):
            return Connection()

    request = Request(
        {
            "type": "http",
            "app": SimpleNamespace(state=SimpleNamespace(engine=Engine())),
        }
    )

    assert await check_db(request) is True


@pytest.mark.asyncio
async def test_check_db_handles_database_error() -> None:
    class FailedConnection:
        async def __aenter__(self):
            raise SQLAlchemyError("Database connection failed")

        async def __aexit__(self, *_: object) -> None:
            return None

    class FailedEngine:
        def connect(self):
            return FailedConnection()

    request = Request(
        {
            "type": "http",
            "app": SimpleNamespace(state=SimpleNamespace(engine=FailedEngine())),
        }
    )

    assert await check_db(request) is False


def test_list_documents_paginates(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"limit": 2})
    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert "filters" not in body


def test_search_filters_records(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"q": "beta"})
    assert [document["id"] for document in response.json()["items"]] == ["002"]


def test_metadata_filter_is_echoed(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"kind": "circular"})
    assert [document["id"] for document in response.json()["items"]] == ["002", "003"]
    assert response.json()["filters"] == {"kind": "circular"}


def test_bad_filter_name_is_problem_details(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"Bad-Name": "1"})
    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"


def test_get_document_found(client: TestClient) -> None:
    response = client.get("/v1/documents/001")
    assert response.status_code == 200
    assert response.json()["title"] == "Alpha guideline"


def test_missing_document_is_problem_details(client: TestClient) -> None:
    response = client.get("/v1/documents/999")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["status"] == 404
    assert body["title"] == "Not Found"
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_bad_limit_is_422_problem(client: TestClient) -> None:
    response = client.get("/v1/documents", params={"limit": 0})
    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "query.limit"


def test_request_id_is_echoed(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "abc123"})
    assert response.headers["X-Request-ID"] == "abc123"


def test_app_refuses_to_start_without_app_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_app_refuses_invalid_app_env() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="prod", _env_file=None)


def test_stats_counts_severity(client: TestClient) -> None:
    response = client.get("/v1/stats")
    assert response.status_code == 200
    assert response.json()["record_count"] == 3
