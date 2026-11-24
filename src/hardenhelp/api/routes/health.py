"""Liveness and readiness endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from hardenhelp.api.deps import check_db

router = APIRouter()


@router.api_route("/health", methods=["GET", "HEAD"])
def health(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "version": settings.git_sha,
    }


@router.get("/ready")
async def ready(
    response: Response,
    database_up: Annotated[bool, Depends(check_db)],
) -> dict[str, object]:
    if not database_up:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if database_up else "not_ready",
        "checks": {"database": database_up},
    }
