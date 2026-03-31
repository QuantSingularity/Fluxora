from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base


class EnergyData(Base):
    __tablename__ = "energy_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consumption_kwh = Column(Float, nullable=False)
    generation_kwh = Column(Float, nullable=True)
    cost_usd = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    owner = relationship("User")

    def __repr__(self) -> Any:
        return f"<EnergyData(id={self.id}, timestamp='{self.timestamp}', consumption={self.consumption_kwh})>"
