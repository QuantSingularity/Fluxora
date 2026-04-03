from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class EnergyDataBase(BaseModel):
    consumption_kwh: float
    generation_kwh: Optional[float] = None
    cost_usd: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None

    @field_validator("consumption_kwh")
    @classmethod
    def consumption_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("consumption_kwh must be non-negative")
        return v

    @field_validator("humidity_percent")
    @classmethod
    def humidity_must_be_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("humidity_percent must be between 0 and 100")
        return v


class EnergyDataCreate(EnergyDataBase):
    pass


class EnergyDataUpdate(BaseModel):
    consumption_kwh: Optional[float] = None
    generation_kwh: Optional[float] = None
    cost_usd: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None


class EnergyData(EnergyDataBase):
    id: int
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True
