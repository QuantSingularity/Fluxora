from datetime import datetime
from typing import Annotated, Any, List

from app.core.security import get_current_active_user
from app.crud.data import (
    create_data_record,
    delete_data_record,
    get_data_by_time_range,
    get_data_record,
    get_data_records,
    update_data_record,
)
from app.db.dependencies import get_db
from app.schemas.data import EnergyData, EnergyDataCreate, EnergyDataUpdate
from app.schemas.user import User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/", response_model=EnergyData, status_code=status.HTTP_201_CREATED)
def create_record(
    data: EnergyDataCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Any:
    """Create a new energy data record."""
    return create_data_record(db=db, data=data, user_id=current_user.id)


@router.get("/", response_model=List[EnergyData])
def read_records(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> Any:
    """List energy data records for the current user."""
    return get_data_records(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/query", response_model=List[EnergyData])
def query_records(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
) -> Any:
    """Query records within a time range."""
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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
    record = get_data_record(db, record_id=record_id, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.patch("/{record_id}", response_model=EnergyData)
def update_record(
    record_id: int,
    data: EnergyDataUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Any:
    """Partially update an energy data record."""
    record = update_data_record(
        db, record_id=record_id, user_id=current_user.id, data=data
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
    deleted = delete_data_record(db, record_id=record_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
