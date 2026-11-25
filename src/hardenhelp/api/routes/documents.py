"""Document routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from hardenhelp.api.deps import get_repo
from hardenhelp.api.errors import problem_response
from hardenhelp.api.schemas import DocumentList, DocumentStats, Record
from hardenhelp.db.repository import FILTER_KEY, DocumentRepository

router = APIRouter()
RepoDependency = Annotated[DocumentRepository, Depends(get_repo)]
RESERVED_QUERY_PARAMETERS = {"limit", "offset", "q"}


@router.get("/documents", response_model=DocumentList, response_model_exclude_none=True)
async def list_documents(
    request: Request,
    repository: RepoDependency,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    q: str | None = None,
) -> dict[str, object]:
    filters = {
        key: value
        for key, value in request.query_params.items()
        if key not in RESERVED_QUERY_PARAMETERS
    }
    bad_keys = [key for key in filters if not FILTER_KEY.fullmatch(key)]
    if bad_keys:
        return problem_response(
            request,
            400,
            "Bad Request",
            f"Invalid filter name: {bad_keys[0]!r}. Use lowercase letters, digits, or underscores.",
        )

    total, items = await repository.list(q=q, filters=filters, limit=limit, offset=offset)
    response = {"total": total, "items": items}
    if filters:
        response["filters"] = filters
    return response


@router.get("/documents/{document_id}", response_model=Record)
async def get_document(
    document_id: str,
    request: Request,
    repository: RepoDependency,
) -> Record | object:
    record = await repository.get(document_id)
    if record is None:
        return problem_response(
            request,
            404,
            "Not Found",
            f"No document with id '{document_id}'.",
        )
    return Record.model_validate(record)


@router.get("/stats", response_model=DocumentStats)
async def stats(repository: RepoDependency) -> dict[str, object]:
    return await repository.stats()
