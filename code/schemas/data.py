from datetime import datetime

from pydantic import BaseModel


class EnergyDataBase(BaseModel):
    consumption_kwh: float
    generation_kwh: float | None = None
    cost_usd: float | None = None
    temperature_c: float | None = None
    humidity_percent: float | None = None


class EnergyDataCreate(EnergyDataBase):
    pass


class EnergyData(EnergyDataBase):
    id: int
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True
