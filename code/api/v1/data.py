from datetime import datetime
from typing import Annotated, Any, List

from backend.dependencies import get_db
from backend.security import get_current_active_user
from crud.data import create_data_record, get_data_by_time_range, get_data_records
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.data import EnergyData, EnergyDataCreate
from schemas.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/", response_model=EnergyData, status_code=status.HTTP_201_CREATED)
def create_record(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    data: EnergyDataCreate,
) -> Any:
    return create_data_record(db=db, data=data, user_id=current_user.id)


@router.get("/", response_model=List[EnergyData])
def read_records(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> Any:
    records = get_data_records(db, user_id=current_user.id, skip=skip, limit=limit)
    return records


@router.get("/query", response_model=List[EnergyData])
def query_records(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    start_time: datetime,
    end_time: datetime,
) -> Any:
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be after start_time",
        )
    records = get_data_by_time_range(
        db, user_id=current_user.id, start_time=start_time, end_time=end_time
    )
    if not records:
        raise HTTPException(
            status_code=404, detail="No data found for the specified time range"
        )
    return records


@router.get("/{record_id}", response_model=EnergyData)
def get_record(
    record_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Any:
    """Retrieve a single data record by ID."""
    from models.data import EnergyData as EnergyDataModel

    record = (
        db.query(EnergyDataModel)
        .filter(
            EnergyDataModel.id == record_id,
            EnergyDataModel.user_id == current_user.id,
        )
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete a single data record by ID."""
    from models.data import EnergyData as EnergyDataModel

    record = (
        db.query(EnergyDataModel)
        .filter(
            EnergyDataModel.id == record_id,
            EnergyDataModel.user_id == current_user.id,
        )
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
