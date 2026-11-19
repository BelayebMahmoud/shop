"""FR-05: user administration. BR-11: there is always at least one active ADMIN."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.services import audit
from app.services.errors import Conflict, NotFound
from app.services.workflow import ADMIN


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)).all())


def _get(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFound("NOT_FOUND")
    return user


def _ensure_another_admin(db: Session, target: User) -> None:
    """Refuse removing the last active ADMIN. Locks the active ADMIN rows so two admins cannot race."""
    if not (target.role == ADMIN and target.is_active):
        return
    admins = db.scalars(select(User.id).where(User.role == ADMIN, User.is_active).with_for_update()).all()
    if len(admins) <= 1:
        raise Conflict("LAST_ADMIN")


def change_role(db: Session, actor: User, user_id: int, role: str) -> User:
    user = _get(db, user_id)
    if role != ADMIN:
        _ensure_another_admin(db, user)
    previous = user.role
    user.role = role
    audit.record(db, actor.id, audit.ROLE_CHANGED, "user", user.id, **{"from": previous, "to": role})
    db.commit()
    return user


def deactivate(db: Session, actor: User, user_id: int) -> User:
    user = _get(db, user_id)
    _ensure_another_admin(db, user)
    user.is_active = False
    audit.record(db, actor.id, audit.USER_DEACTIVATED, "user", user.id)
    db.commit()
    return user
