from typing import Any, List

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    energy_records: List[Any] = relationship(
        "EnergyData", back_populates="owner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> Any:
        return f"<User(id={self.id}, email='{self.email}')>"
