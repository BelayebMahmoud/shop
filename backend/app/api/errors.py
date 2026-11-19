"""Map domain errors to HTTP. Body: {"detail": {"code": ..., <extra fields>}}. A 500 never leaks internals."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

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

    @app.exception_handler(Exception)
    async def unexpected(_: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": {"code": "INTERNAL_ERROR"}})
