"""Map domain errors to HTTP. Body: {"detail": {"code": ..., <extra fields>}}. A 500 never leaks internals."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import InterfaceError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import route_table
from app.services.errors import Conflict, DomainError, Forbidden, InvalidInput, NotFound

log = logging.getLogger("app")

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    InvalidInput: status.HTTP_422_UNPROCESSABLE_CONTENT,
    Forbidden: status.HTTP_403_FORBIDDEN,
    NotFound: status.HTTP_404_NOT_FOUND,
    Conflict: status.HTTP_409_CONFLICT,
}


def install(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error(_: Request, exc: DomainError) -> JSONResponse:
        code = STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=code, content={"detail": {"code": exc.code, **exc.extra}})

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        headers = dict(exc.headers or {})
        if exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            # ANO-04: list every method of every route on this path, not only the first route's.
            found = route_table.match(app, request.url.path)
            headers["Allow"] = ", ".join(sorted(found[1])) if found else ""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=headers)

    @app.exception_handler(OperationalError)
    @app.exception_handler(InterfaceError)
    async def database_unavailable(_: Request, exc: Exception) -> JSONResponse:
        # QR-RE-01: while PostgreSQL is down or restarting, answer 503 (temporary, retry) rather than 500.
        log.warning("database unavailable: %s", type(exc).__name__)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": {"code": "DATABASE_UNAVAILABLE"}},
            headers={"Retry-After": "5"},
        )

    @app.exception_handler(Exception)
    async def unexpected(_: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": {"code": "INTERNAL_ERROR"}})
