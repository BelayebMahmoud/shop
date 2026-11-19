"""Constrained input types shared by routes and schemas (fixes ANO-01, ANO-02, ANO-03 of docs/anomalies.md).

- ids fit PostgreSQL BIGINT, money and stock fit INTEGER: an out-of-range number is a 422, never a 500;
- text never contains NUL (0x00), which PostgreSQL cannot store;
- integers follow JSON Schema (`409.0` is 409; `false` and `"409"` are refused);
- dates must be ISO `YYYY-MM-DD` (`0` is not 1970-01-01).
"""

import re
from datetime import date
from typing import Annotated

from fastapi import Path, Query
from pydantic import BeforeValidator, Field

BIGINT_MAX = 2**63 - 1  # PostgreSQL BIGINT
MAX_ID = 2**53 - 1  # largest integer a JavaScript client holds exactly; exact in OpenAPI too (ANO-01)
INT_MAX = 2**31 - 1
NO_NUL = r"^[^\x00]*$"
# Explicit whitespace: Python `\s` also matches U+0085 and others, JSON Schema (ECMA-262) does not.
SPACE = r" \t\n\r\f\v"
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _iso_date_only(value: object) -> object:
    if isinstance(value, str) and not ISO_DATE.match(value):
        raise ValueError("date must be YYYY-MM-DD")
    if not isinstance(value, (str, date)):
        raise ValueError("date must be YYYY-MM-DD")
    return value


def _json_integer(value: object) -> object:
    """JSON Schema integers: 409 and 409.0 are integers; true/false and "409" are not (ANO-03)."""
    if isinstance(value, (bool, str)):
        raise ValueError("must be a JSON integer")
    return value


def json_int(ge: int, le: int) -> object:
    # Bounds sit on the int itself so OpenAPI publishes them as minimum/maximum.
    return Annotated[int, Field(ge=ge, le=le), BeforeValidator(_json_integer)]


# Body fields
DbId = json_int(1, MAX_ID)
Cents = json_int(0, 100_000_000)
Stock = json_int(0, 1_000_000)

# Path and query parameters
IdPath = Annotated[int, Path(ge=1, le=MAX_ID)]
IdQuery = Annotated[int | None, Query(ge=1, le=MAX_ID)]
CentsQuery = Annotated[int | None, Query(ge=0, le=INT_MAX)]
TextQuery = Annotated[str | None, Query(max_length=100, pattern=NO_NUL)]
IsoDateQuery = Annotated[date | None, BeforeValidator(_iso_date_only), Query()]
