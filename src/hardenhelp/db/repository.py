"""All SQL for documents lives here. Endpoints never write SQL themselves."""

import re
from typing import Any

from sqlalchemy import Text, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from hardenhelp.db.models import Document

FILTER_KEY = re.compile(r"^[a-z_][a-z0-9_]{0,40}$")


def _visible_documents():
    """Exclude documents explicitly marked as quarantined."""
    return ~Document.metadata_.contains({"quarantined": True})


def to_dict(document: Document) -> dict[str, Any]:
    return {
        "id": document.external_id,
        **document.metadata_,
        "title": document.title,
        "doc_type": document.doc_type,
        "source_url": document.source_url,
        "licence": document.licence,
        "published_on": document.published_on.isoformat() if document.published_on else None,
    }


def _value_candidates(value: str) -> list[Any]:
    candidates: list[Any] = [value, [value]]
    lowered = value.lower()

    if lowered in {"true", "false"}:
        candidates.append(lowered == "true")
    elif re.fullmatch(r"-?\d+", value):
        candidates.append(int(value))
    elif re.fullmatch(r"-?\d+\.\d+", value):
        candidates.append(float(value))

    return candidates


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        *,
        q: str | None,
        filters: dict[str, str],
        limit: int,
        offset: int,
    ) -> tuple[int, list[dict[str, Any]]]:
        statement = select(Document).where(_visible_documents())

        if q:
            pattern = f"%{q}%"
            statement = statement.where(
                or_(
                    Document.title.ilike(pattern),
                    cast(Document.metadata_, Text).ilike(pattern),
                )
            )

        for key, value in filters.items():
            statement = statement.where(
                or_(
                    *(
                        Document.metadata_.contains({key: candidate})
                        for candidate in _value_candidates(value)
                    )
                )
            )

        total = await self.session.scalar(select(func.count()).select_from(statement.subquery()))

        documents = await self.session.scalars(
            statement.order_by(Document.external_id).limit(limit).offset(offset)
        )

        return total or 0, [to_dict(document) for document in documents]

    async def get(self, external_id: str) -> dict[str, Any] | None:
        document = await self.session.scalar(
            select(Document).where(
                Document.external_id == external_id,
                _visible_documents(),
            )
        )

        return to_dict(document) if document else None

    async def stats(self) -> dict[str, Any]:
        severity = Document.metadata_["severity"].as_string()

        rows = await self.session.execute(
            select(severity, func.count()).where(_visible_documents()).group_by(severity)
        )

        counts = {value or "unknown": count for value, count in rows}

        total = await self.session.scalar(
            select(func.count()).select_from(Document).where(_visible_documents())
        )

        return {
            "record_count": total or 0,
            "severity_counts": counts,
        }
