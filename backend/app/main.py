from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import errors as error_handlers
from app.api.deps import get_db
from app.api.responses import errors
from app.api.routes import admin, auth, catalog, orders

app = FastAPI(title="Gestion commerciale", version="0.2.0", responses=errors(503))  # every route: DB down -> 503
error_handlers.install(app)

# The API is also reachable directly (port 8000), not only through nginx: it sets its own security headers
# (ZAP 10021 X-Content-Type-Options, 90004 Cross-Origin-Resource-Policy — docs/securite/triage.md).
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Referrer-Policy": "no-referrer",
}


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    return response


for router in (
    auth.router,
    catalog.categories,
    catalog.products,
    orders.router,
    admin.users_router,
    admin.dashboard_router,
    admin.audit_router,
):
    app.include_router(router, prefix="/api")


@app.get("/api/health", tags=["meta"], responses=errors(503))
def health(db: Session = Depends(get_db)) -> JSONResponse:
    """200 when the database answers, 503 while it is down (QR-RE-01)."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "unavailable", "database": "down"})
    return JSONResponse(content={"status": "ok", "database": "ok"})
