"""Documented error responses, so the OpenAPI contract lists every status a route can return (QR-CO-02)."""

from typing import Any

from pydantic import BaseModel


class ErrorBody(BaseModel):
    """Business and permission errors: {"detail": {"code": "OUT_OF_STOCK", ...}}."""

    detail: dict[str, Any]


class MessageErrorBody(BaseModel):
    """401 and 400: {"detail": "Invalid or expired token"} / {"detail": "There was an error parsing the body"}."""

    detail: str


class UnprocessableBody(BaseModel):
    """422: field errors from validation (list) or a rule on a value range (object with a code)."""

    detail: list[dict[str, Any]] | dict[str, Any]


DESCRIPTIONS = {
    400: "Body could not be parsed",
    401: "Missing, invalid or expired token",
    403: "Role not allowed",
    404: "Not found (or another customer's order)",
    409: "Business rule refused the action",
    422: "Invalid input",
    503: "Database unavailable",
}
MODELS = {400: MessageErrorBody, 401: MessageErrorBody, 422: UnprocessableBody}


def errors(*codes: int) -> dict[int | str, dict[str, Any]]:
    return {code: {"model": MODELS.get(code, ErrorBody), "description": DESCRIPTIONS[code]} for code in codes}
