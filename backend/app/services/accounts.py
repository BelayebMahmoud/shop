"""FR-01: registration, login (audited) and loading the current user (Q-08: deactivated -> refused)."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User
from app.services import audit
from app.services.errors import Conflict


def register(db: Session, email: str, password: str) -> User:
    email = email.lower()
    if db.scalar(select(User.id).where(func.lower(User.email) == email)):
        raise Conflict("DUPLICATE", field="email")
    user = User(email=email, password_hash=hash_password(password), role="CUSTOMER")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    """Return the user on success. Success and failure are both written to the audit log."""
    email = email.lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    ok = user is not None and user.is_active and verify_password(password, user.password_hash)
    if ok:
        audit.record(db, user.id, audit.LOGIN_SUCCESS, "user", user.id)
    else:
        audit.record(db, user.id if user else None, audit.LOGIN_FAILURE, "user", user.id if user else None, email=email)
    db.commit()
    return user if ok else None


def active_user(db: Session, user_id: int) -> User | None:
    """The role and the active flag are read from the database on every request (SEC-04, Q-08)."""
    user = db.get(User, user_id)
    return user if user is not None and user.is_active else None
