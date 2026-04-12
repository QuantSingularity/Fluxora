from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class EnergyData(Base):
    __tablename__ = "energy_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
        nullable=False,
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consumption_kwh = Column(Float, nullable=False)
    generation_kwh = Column(Float, nullable=True)
    cost_usd = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    owner = relationship("User", back_populates="energy_records")

    def __repr__(self) -> str:
        return (
            f"<EnergyData(id={self.id}, timestamp='{self.timestamp}', "
            f"consumption={self.consumption_kwh})>"
        )
