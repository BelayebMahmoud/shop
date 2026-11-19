from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import errors
from app.api.deps import get_db
from app.api.routes import admin, auth, catalog, orders

app = FastAPI(title="Gestion commerciale", version="0.2.0")
errors.install(app)

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


@app.get("/api/health", tags=["meta"])
def health(db: Session = Depends(get_db)) -> JSONResponse:
    """200 when the database answers, 503 while it is down (QR-RE-01)."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "unavailable", "database": "down"})
    return JSONResponse(content={"status": "ok", "database": "ok"})
