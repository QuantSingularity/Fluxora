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

    @field_validator("generation_kwh")
    @classmethod
    def generation_must_be_non_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("generation_kwh must be non-negative")
        return v

    @field_validator("cost_usd")
    @classmethod
    def cost_must_be_non_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("cost_usd must be non-negative")
        return v

    @field_validator("humidity_percent")
    @classmethod
    def humidity_must_be_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("humidity_percent must be between 0 and 100")
        return v

    @field_validator("temperature_c")
    @classmethod
    def temperature_must_be_in_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-100.0 <= v <= 100.0):
            raise ValueError("temperature_c must be between -100 and 100")
        return v


class EnergyDataCreate(EnergyDataBase):
    timestamp: Optional[datetime] = None


class EnergyDataUpdate(BaseModel):
    consumption_kwh: Optional[float] = None
    generation_kwh: Optional[float] = None
    cost_usd: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None

    @field_validator("consumption_kwh")
    @classmethod
    def consumption_must_be_non_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("consumption_kwh must be non-negative")
        return v


class EnergyData(EnergyDataBase):
    id: int
    timestamp: datetime
    user_id: int

    model_config = {"from_attributes": True}
