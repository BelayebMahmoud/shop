"""FR-11: audit entries. `record` only adds to the session: the caller commits it with the action itself."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog
from app.services.errors import NotFound

LOGIN_SUCCESS = "LOGIN_SUCCESS"
LOGIN_FAILURE = "LOGIN_FAILURE"
ORDER_CREATED = "ORDER_CREATED"
ORDER_STATUS_CHANGED = "ORDER_STATUS_CHANGED"
ORDER_CANCELLED = "ORDER_CANCELLED"
PRODUCT_CREATED = "PRODUCT_CREATED"
PRODUCT_UPDATED = "PRODUCT_UPDATED"
PRODUCT_DELETED = "PRODUCT_DELETED"
ROLE_CHANGED = "ROLE_CHANGED"
USER_DEACTIVATED = "USER_DEACTIVATED"


def record(db: Session, actor_id: int | None, action: str, entity: str, entity_id: int | None, **details: Any) -> None:
    db.add(AuditLog(actor_id=actor_id, action=action, entity=entity, entity_id=entity_id, details=details))


def list_entries(db: Session, limit: int, offset: int) -> list[AuditLog]:
    stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


def get_entry(db: Session, entry_id: int) -> AuditLog:
    entry = db.get(AuditLog, entry_id)
    if entry is None:
        raise NotFound("NOT_FOUND")
    return entry
