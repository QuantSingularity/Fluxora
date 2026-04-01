from typing import Generator

from sqlalchemy.orm import Session

from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_direct() -> Session:
    """
    Returns a database session directly (not as a generator).
    Caller is responsible for closing the session.
    """
    return SessionLocal()
