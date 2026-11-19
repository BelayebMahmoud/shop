from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.responses import errors
from app.api.schemas import Token, UserCreate, UserOut
from app.core.security import create_access_token
from app.models import User
from app.services import accounts
from app.services.errors import InvalidInput

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, responses=errors(400, 409, 422))
def register(body: UserCreate, db: Session = Depends(get_db)) -> User:
    return accounts.register(db, body.email, body.password)


@router.post("/login", response_model=Token, responses=errors(400, 401, 422))
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    if "\x00" in form.username or "\x00" in form.password:  # ANO-02: PostgreSQL text cannot hold NUL
        raise InvalidInput("NUL_CHARACTER")
    user = accounts.authenticate(db, form.username, form.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=create_access_token(user.id))


@router.get(
    "/me",
    response_model=UserOut,
    responses=errors(401),
)
def me(user: User = Depends(get_current_user)) -> User:
    return user
