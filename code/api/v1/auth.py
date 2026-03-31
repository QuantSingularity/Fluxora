from datetime import timedelta
from typing import Annotated, Any

from backend.dependencies import get_db
from backend.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    verify_password,
)
from crud.user import get_user_by_email
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user import Token, User, UserCreate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Any:
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    from crud.user import create_user

    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db=db, user=user)
    return new_user
