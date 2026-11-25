"""Persist parsed documents and parsing failures in PostgreSQL."""

import hashlib
from pathlib import Path
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from hardenhelp.db.models import Document, Page, ParseFailure
from hardenhelp.ingest.parse import ParsedDoc


def file_sha256(path: Path) -> str:
    """Return the SHA-256 fingerprint of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def save_parsed(
    session: AsyncSession,
    *,
    path: Path,
    record: dict[str, Any],
    parsed: ParsedDoc,
) -> Document:
    """Save a parsed document and replace its pages idempotently."""
    sha256 = file_sha256(path)
    external_id = sha256

    metadata = {
        "path": str(path),
        "parser": parsed.parser,
        "pages": len(parsed.pages),
        "tables": sum(page.tables for page in parsed.pages),
        "scanned_pages": parsed.scanned_pages,
        "source": record.get("source"),
        "download_url": record.get("download_url"),
    }

    document = await session.scalar(select(Document).where(Document.external_id == external_id))

    if document is None:
        document = Document(
            external_id=external_id,
            title=parsed.title or record.get("title") or path.name,
            source_url=record.get("url"),
            licence=record.get("licence"),
            doc_type=parsed.kind,
            sha256=sha256,
            metadata_=metadata,
        )
        session.add(document)
        await session.flush()
    else:
        document.title = parsed.title or record.get("title") or path.name
        document.source_url = record.get("url")
        document.licence = record.get("licence")
        document.doc_type = parsed.kind
        document.sha256 = sha256
        document.metadata_ = metadata

        await session.execute(delete(Page).where(Page.document_id == document.id))

    session.add_all(
        [
            Page(
                document_id=document.id,
                page_no=page.page_no,
                text=page.text,
                headings=page.headings,
            )
            for page in parsed.pages
        ]
    )

    await session.execute(delete(ParseFailure).where(ParseFailure.path == str(path)))
    await session.flush()

    return document


async def save_failure(
    session: AsyncSession,
    *,
    path: Path,
    record: dict[str, Any],
    reason: str,
    detail: str = "",
) -> None:
    """Insert a parse failure or update its details and attempt count."""
    sha256 = file_sha256(path) if path.is_file() else hashlib.sha256(b"").hexdigest()

    statement = insert(ParseFailure).values(
        path=str(path),
        sha256=sha256,
        source_url=record.get("url"),
        reason=reason[:40],
        detail=detail[:500],
        attempts=1,
    )

    statement = statement.on_conflict_do_update(
        index_elements=[ParseFailure.path],
        set_={
            "sha256": statement.excluded.sha256,
            "source_url": statement.excluded.source_url,
            "reason": statement.excluded.reason,
            "detail": statement.excluded.detail,
            "attempts": ParseFailure.attempts + 1,
            "updated_at": func.now(),
        },
    )

    await session.execute(statement)
    await session.flush()
