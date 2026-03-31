from typing import Any

from backend.security import get_password_hash
from models.user import User
from schemas.user import UserCreate
from sqlalchemy.orm import Session


def get_user(db: Session, user_id: int) -> Any:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Any:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> Any:
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
