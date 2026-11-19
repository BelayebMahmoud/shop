"""Users (FR-05), dashboard (FR-09) and audit log (FR-11)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.api.responses import errors
from app.api.types import IdPath, IdQuery, IsoDateQuery
from app.api.schemas import AuditOut, DashboardOut, LowStockProduct, RoleChange, TopProduct, UserOut
from app.models import AuditLog, User
from app.services import audit, dashboard, users
from app.services.workflow import ADMIN, STAFF

users_router = APIRouter(prefix="/users", tags=["users"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])
audit_router = APIRouter(prefix="/audit", tags=["audit"])
admin_only = require_roles(ADMIN)


@users_router.get("", response_model=list[UserOut], responses=errors(401, 403))
def list_users(_: User = Depends(admin_only), db: Session = Depends(get_db)) -> list[User]:
    return users.list_users(db)


@users_router.patch("/{user_id}/role", response_model=UserOut, responses=errors(400, 401, 403, 404, 409, 422))
def change_role(user_id: IdPath, body: RoleChange, actor: User = Depends(admin_only), db: Session = Depends(get_db)) -> User:
    return users.change_role(db, actor, user_id, body.role)


@users_router.patch("/{user_id}/deactivate", response_model=UserOut, responses=errors(401, 403, 404, 409, 422))
def deactivate(user_id: IdPath, actor: User = Depends(admin_only), db: Session = Depends(get_db)) -> User:
    return users.deactivate(db, actor, user_id)


@dashboard_router.get("", response_model=DashboardOut, responses=errors(401, 403, 422))
def get_dashboard(
    date_from: IsoDateQuery = None,
    date_to: IsoDateQuery = None,
    category_id: IdQuery = None,
    _: User = Depends(require_roles(STAFF, ADMIN)),
    db: Session = Depends(get_db),
) -> DashboardOut:
    d = dashboard.compute(db, date_from, date_to, category_id)
    return DashboardOut(
        revenue_cents=d.revenue_cents,
        orders_by_status=d.orders_by_status,
        top_products=[TopProduct(product_id=pid, name=name, quantity=qty) for pid, name, qty in d.top_products],
        low_stock=[LowStockProduct.model_validate(p) for p in d.low_stock],
        low_stock_total=d.low_stock_total,
    )


@audit_router.get("", response_model=list[AuditOut], responses=errors(401, 403, 422))
def list_audit(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0, le=1_000_000_000),
    _: User = Depends(admin_only),
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    return audit.list_entries(db, limit, offset)


@audit_router.get("/{entry_id}", response_model=AuditOut, responses=errors(401, 403, 404, 422))
def get_audit(entry_id: IdPath, _: User = Depends(admin_only), db: Session = Depends(get_db)) -> AuditLog:
    # Read-only on purpose: no PUT or DELETE route exists, so those methods answer 405 (FR-11).
    return audit.get_entry(db, entry_id)
