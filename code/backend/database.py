import os
from typing import Any

from models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fluxora.db")

# Handle SQLite specific connection args
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> Any:
    """Initializes the database by creating all tables."""
    # Import all models here to ensure they're registered with Base

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
