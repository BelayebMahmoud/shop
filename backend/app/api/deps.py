"""Request dependencies: database session, current user, role checks (identity -> role, before shape)."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models import User
from app.services import accounts
from app.services.errors import Forbidden

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

__all__ = ["get_db", "get_current_user", "require_roles"]


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_access_token(token)
    user = accounts.active_user(db, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed = frozenset(roles)

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise Forbidden("FORBIDDEN", required=sorted(allowed))
        return user

    return dependency
