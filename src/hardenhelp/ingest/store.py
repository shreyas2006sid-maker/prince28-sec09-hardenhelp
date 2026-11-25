"""Save parsed documents and record parsing failures."""

import hashlib
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from hardenhelp.db.models import Document, Page, ParseFailure
from hardenhelp.ingest.parse import ParsedDoc, ParseError


def document_id(sha256: str) -> str:
    """Files are identified by their content."""
    return f"f-{sha256[:20]}"


def file_hash(path: Path) -> str:
    """Calculate the SHA-256 hash of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def parsed_ids(session: AsyncSession) -> set[str]:
    rows = await session.scalars(
        select(Document.external_id).where(Document.doc_type != "record")
    )
    return set(rows)


async def failed_paths(session: AsyncSession) -> set[str]:
    return set(await session.scalars(select(ParseFailure.path)))


async def save_parsed(
    session: AsyncSession,
    *,
    path: Path,
    record: dict,
    parsed: ParsedDoc,
) -> Document:
    """Save a parsed document and its pages without creating duplicates."""
    own_transaction = not session.in_transaction()

    file_path = str(path)
    sha256 = file_hash(path)
    external_id = document_id(sha256)

    title = parsed.title or record.get("title") or path.stem

    metadata = {
        "source": record.get("source", ""),
        "path": file_path,
        "parser": parsed.parser,
        "pages": len(parsed.pages),
        "tables": sum(page.tables for page in parsed.pages),
        "chars": sum(len(page.text) for page in parsed.pages),
        "scanned_pages": parsed.scanned_pages,
    }

    document = await session.scalar(
        select(Document).where(Document.external_id == external_id)
    )

    if document is None:
        document = Document(
            external_id=external_id,
            title=title[:500],
            source_url=record.get("url"),
            licence=(record.get("licence") or "")[:200],
            doc_type=parsed.kind,
            sha256=sha256,
            metadata_=metadata,
        )
        session.add(document)
        await session.flush()
    else:
        document.title = title[:500]
        document.source_url = record.get("url")
        document.licence = (record.get("licence") or "")[:200]
        document.doc_type = parsed.kind
        document.sha256 = sha256
        document.metadata_ = metadata

        await session.execute(
            delete(Page).where(Page.document_id == document.id)
        )
        await session.flush()

    for page in parsed.pages:
        session.add(
            Page(
                document_id=document.id,
                page_no=page.page_no,
                text=page.text,
                headings=page.headings,
            )
        )

    await session.execute(
        delete(ParseFailure).where(ParseFailure.path == file_path)
    )

    if own_transaction:
        await session.commit()
    else:
        await session.flush()

    await session.refresh(document)
    return document


async def save_document(
    session: AsyncSession,
    record: dict,
    parsed: ParsedDoc,
) -> Document:
    """Backward-compatible wrapper for the corpus workflow."""
    return await save_parsed(
        session,
        path=Path(record["path"]),
        record=record,
        parsed=parsed,
    )


async def save_failure(
    session: AsyncSession,
    record: dict,
    error: ParseError | None = None,
    *,
    path: Path | None = None,
    reason: str | None = None,
    detail: str = "",
) -> None:
    """Insert a parse failure or increment its retry count."""
    own_transaction = not session.in_transaction()

    if path is None:
        path = Path(record["path"])

    if error is not None:
        reason = error.reason
        detail = error.detail

    if reason is None:
        raise ValueError("A parse failure reason is required.")

    sha256 = (
        record["sha256"]
        if record.get("sha256")
        else file_hash(path)
    )

    row = {
        "path": str(path),
        "sha256": sha256,
        "source_url": record.get("url"),
        "reason": reason,
        "detail": detail,
    }

    statement = insert(ParseFailure).values(**row)
    statement = statement.on_conflict_do_update(
        index_elements=[ParseFailure.path],
        set_={
            "sha256": sha256,
            "source_url": row["source_url"],
            "reason": reason,
            "detail": detail,
            "attempts": ParseFailure.attempts + 1,
        },
    )

    await session.execute(statement)

    if own_transaction:
        await session.commit()
    else:
        await session.flush()
