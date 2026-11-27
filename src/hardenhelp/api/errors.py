"""RFC 9457 problem-details responses."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def problem_response(
    request: Request,
    status: int,
    title: str,
    detail: str,
    *,
    errors: list[dict[str, str]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    request_id = getattr(
        request.state,
        "request_id",
        request.headers.get("x-request-id"),
    )

    body: dict[str, object] = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "request_id": request_id,
    }

    if errors is not None:
        body["errors"] = errors

    response_headers = dict(headers or {})
    response_headers["Content-Type"] = "application/problem+json"
    response_headers["X-Request-ID"] = str(request_id)

    return JSONResponse(
        status_code=status,
        content=body,
        headers=response_headers,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = []

    for error in exc.errors():
        loc = ".".join(str(part) for part in error["loc"])
        errors.append({"field": loc, "message": error["msg"]})

    return problem_response(
        request,
        422,
        "Unprocessable Content",
        "One or more request parameters are invalid.",
        errors=errors,
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Convert HTTP errors into RFC 9457 problem-details responses."""
    return problem_response(
        request,
        exc.status_code,
        "HTTP Error",
        str(exc.detail),
        headers=exc.headers,
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers."""
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
