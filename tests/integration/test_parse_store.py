from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from hardenhelp.db.models import Document, Page, ParseFailure
from hardenhelp.ingest.parse import ParsedDoc, ParsedPage
from hardenhelp.ingest.store import save_failure, save_parsed


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    path = tmp_path / "guide.md"
    path.write_text(
        "# Security Guide\n\nThis is a security document.",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def record() -> dict[str, str]:
    return {
        "url": "https://example.com/guide",
        "licence": "CC-BY-4.0",
        "source": "Example",
        "download_url": "https://example.com/guide.md",
        "title": "Security Guide",
    }


@pytest.fixture
def parsed() -> ParsedDoc:
    return ParsedDoc(
        parser="plain",
        kind="text",
        title="Security Guide",
        pages=[
            ParsedPage(
                page_no=1,
                text="# Security Guide\n\nThis is a security document.",
                headings=[],
                tables=0,
            ),
            ParsedPage(
                page_no=2,
                text="Additional security information.",
                headings=["Security Guide"],
                tables=0,
            ),
        ],
    )


@pytest.fixture
async def session(database_url: str):
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as db, db.begin():
            yield db
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_save_parsed_creates_document_and_pages(
    session,
    source_file: Path,
    record: dict[str, str],
    parsed: ParsedDoc,
):
    document = await save_parsed(
        session,
        path=source_file,
        record=record,
        parsed=parsed,
    )

    saved_document = await session.get(Document, document.id)
    pages = list(
        (
            await session.scalars(
                select(Page).where(Page.document_id == document.id).order_by(Page.page_no)
            )
        ).all()
    )

    assert saved_document is not None
    assert saved_document.title == "Security Guide"
    assert saved_document.doc_type == "text"
    assert len(pages) == 2
    assert pages[1].headings == ["Security Guide"]


@pytest.mark.asyncio
async def test_save_parsed_is_idempotent(
    session,
    source_file: Path,
    record: dict[str, str],
    parsed: ParsedDoc,
):
    first = await save_parsed(
        session,
        path=source_file,
        record=record,
        parsed=parsed,
    )

    second = await save_parsed(
        session,
        path=source_file,
        record=record,
        parsed=parsed,
    )

    documents = list(
        (
            await session.scalars(select(Document).where(Document.external_id == first.external_id))
        ).all()
    )
    pages = list((await session.scalars(select(Page).where(Page.document_id == second.id))).all())

    assert first.id == second.id
    assert len(documents) == 1
    assert len(pages) == 2


@pytest.mark.asyncio
async def test_save_failure_records_and_increments_attempts(
    session,
    source_file: Path,
    record: dict[str, str],
):
    await save_failure(
        session,
        path=source_file,
        record=record,
        reason="no_text_layer",
        detail="The PDF needs OCR.",
    )

    await save_failure(
        session,
        path=source_file,
        record=record,
        reason="no_text_layer",
        detail="Retry also needs OCR.",
    )

    failure = await session.scalar(
        select(ParseFailure).where(ParseFailure.path == str(source_file))
    )

    assert failure is not None
    assert failure.reason == "no_text_layer"
    assert failure.attempts == 2
    assert failure.detail == "Retry also needs OCR."
