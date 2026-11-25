import hashlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from hardenhelp.api.main import create_app
from hardenhelp.config import Settings, get_settings
from hardenhelp.db.models import Document
from hardenhelp.db.repository import DocumentRepository
from hardenhelp.db.session import make_engine, make_sessionmaker
from scripts.load_db import main as load_database

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROWS = [
    {"id": "001", "title": "Alpha", "kind": "circular", "year": 2024, "tags": ["a", "b"]},
    {"id": "002", "title": "Beta", "kind": "guideline", "year": 2025, "tags": ["b"]},
    {"id": "003", "title": "Gamma", "kind": "circular", "year": 2025, "tags": []},
]


@pytest.fixture
def settings(database_url: str) -> Settings:
    return Settings(app_env="ci", database_url=database_url, _env_file=None)


@pytest.fixture
async def seeded(settings: Settings) -> Settings:
    engine = make_engine(settings)
    try:
        async with make_sessionmaker(engine)() as session, session.begin():
            await session.execute(text("DELETE FROM documents"))
            filler_rows = [
                {
                    "id": f"seed-{index:03}",
                    "title": f"Seed {index:03}",
                    "kind": "other",
                    "year": 2020,
                    "tags": [],
                }
                for index in range(17)
            ]
            for row in [*ROWS, *filler_rows]:
                metadata = {key: value for key, value in row.items() if key not in ("id", "title")}
                digest = hashlib.sha256(
                    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest()
                session.add(
                    Document(
                        external_id=row["id"],
                        title=row["title"],
                        sha256=digest,
                        metadata_=metadata,
                    )
                )
    finally:
        await engine.dispose()
    return settings


@pytest.mark.asyncio
async def test_migrations_created_the_tables(settings: Settings) -> None:
    engine = make_engine(settings)
    try:
        async with engine.connect() as connection:
            tables = set(
                await connection.scalars(
                    text(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'public'"
                    )
                )
            )
            version = await connection.scalar(text("SELECT version_num FROM alembic_version"))
    finally:
        await engine.dispose()

    assert {"documents", "pages", "alembic_version"} <= tables
    assert version


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        ({"kind": "circular"}, ["001", "003"]),
        ({"year": "2025"}, ["002", "003"]),
        ({"tags": "b"}, ["001", "002"]),
        ({"kind": "circular", "year": "2025"}, ["003"]),
    ],
)
@pytest.mark.asyncio
async def test_repository_filters(
    seeded: Settings,
    filters: dict[str, str],
    expected: list[str],
) -> None:
    engine = make_engine(seeded)
    try:
        async with make_sessionmaker(engine)() as session:
            total, items = await DocumentRepository(session).list(
                q=None, filters=filters, limit=10, offset=0
            )
    finally:
        await engine.dispose()

    assert [item["id"] for item in items] == expected
    assert total == len(expected)


def test_api_against_real_database(seeded: Settings) -> None:
    with TestClient(create_app(seeded)) as client:
        readiness = client.get("/ready")
        document = client.get("/v1/documents/002")
        search = client.get("/v1/documents", params={"q": "gamm"})

    assert readiness.status_code == 200
    assert readiness.json()["checks"]["database"] is True
    assert document.status_code == 200
    assert document.json()["title"] == "Beta"
    assert search.status_code == 200
    assert search.json()["total"] == 1


@pytest.mark.asyncio
async def test_loader_is_idempotent(
    database_url: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    data = tmp_path / "records.json"
    data.write_text(
        json.dumps([{"id": "L1", "x": 1}, {"id": "L2", "x": 2}]),
        encoding="utf-8",
    )

    monkeypatch.setenv("APP_ENV", "ci")
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("DATA_FILE", str(data))

    get_settings.cache_clear()

    try:
        await load_database()
        first_output = capsys.readouterr().out

        await load_database()
        second_output = capsys.readouterr().out

        assert "inserted=2" in first_output
        assert "inserted=0 updated=0 unchanged=2" in second_output
    finally:
        get_settings.cache_clear()
