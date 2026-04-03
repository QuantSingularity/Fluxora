import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fluxora.db")

connect_args: dict = {}
engine_kwargs: dict = {"pool_pre_ping": True}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL / MySQL – use a bounded connection pool
    engine_kwargs["pool_size"] = int(os.getenv("DB_POOL_SIZE", "5"))
    engine_kwargs["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "10"))

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initializes the database by creating all tables."""
    import models.data  # noqa: F401  – registers EnergyData model
    import models.user  # noqa: F401  – registers User model
    from models.base import Base

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised.")


if __name__ == "__main__":
    init_db()
