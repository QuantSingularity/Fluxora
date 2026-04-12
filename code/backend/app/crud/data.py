from datetime import datetime
from typing import List, Optional

from app.models.data import EnergyData
from app.schemas.data import EnergyDataCreate, EnergyDataUpdate
from sqlalchemy.orm import Session


def get_data_records(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[EnergyData]:
    return (
        db.query(EnergyData)
        .filter(EnergyData.user_id == user_id)
        .order_by(EnergyData.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_data_record(db: Session, record_id: int, user_id: int) -> Optional[EnergyData]:
    return (
        db.query(EnergyData)
        .filter(EnergyData.id == record_id, EnergyData.user_id == user_id)
        .first()
    )


def create_data_record(db: Session, data: EnergyDataCreate, user_id: int) -> EnergyData:
    data_dict = data.model_dump(exclude_unset=False)
    # Remove None timestamp so model default applies
    if data_dict.get("timestamp") is None:
        data_dict.pop("timestamp", None)
    db_data = EnergyData(**data_dict, user_id=user_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def update_data_record(
    db: Session, record_id: int, user_id: int, data: EnergyDataUpdate
) -> Optional[EnergyData]:
    record = get_data_record(db, record_id=record_id, user_id=user_id)
    if record is None:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def delete_data_record(db: Session, record_id: int, user_id: int) -> bool:
    record = get_data_record(db, record_id=record_id, user_id=user_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True


def get_data_by_time_range(
    db: Session, user_id: int, start_time: datetime, end_time: datetime
) -> List[EnergyData]:
    return (
        db.query(EnergyData)
        .filter(
            EnergyData.user_id == user_id,
            EnergyData.timestamp >= start_time,
            EnergyData.timestamp <= end_time,
        )
        .order_by(EnergyData.timestamp)
        .all()
    )


def count_data_records(db: Session, user_id: int) -> int:
    return db.query(EnergyData).filter(EnergyData.user_id == user_id).count()
