"""Route templates and their methods, read from the app's own OpenAPI document.

FastAPI keeps included routers as nested objects, so `app.routes` does not list every endpoint; the OpenAPI
paths do. Used for the 405 `Allow` header (ANO-04) and by the tests to name the route a request hit.
"""

import re
from functools import cache

from fastapi import FastAPI

_PARAM = re.compile(r"\{[^/{}]+\}")


@cache
def _table(app: FastAPI) -> tuple[tuple[re.Pattern[str], str, frozenset[str]], ...]:
    rows = []
    for template, operations in app.openapi()["paths"].items():
        regex = re.compile("^" + _PARAM.sub("[^/]+", re.escape(template).replace(r"\{", "{").replace(r"\}", "}")) + "$")
        rows.append((regex, template, frozenset(m.upper() for m in operations)))
    return tuple(rows)


def match(app: FastAPI, path: str) -> tuple[str, frozenset[str]] | None:
    """(route template, allowed methods) for a concrete path, or None if no route has this path."""
    for regex, template, methods in _table(app):
        if regex.match(path):
            return template, methods
    return None
