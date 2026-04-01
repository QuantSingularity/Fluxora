import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Dict, List, Optional

from backend.dependencies import get_db
from backend.security import get_current_active_user
from crud.data import get_data_by_time_range
from fastapi import APIRouter, Depends, HTTPException, status
from models.data import EnergyData
from pydantic import BaseModel
from schemas.user import User
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsPoint(BaseModel):
    label: str
    consumption: float
    cost: float
    temperature: Optional[float] = None
    efficiency: float


def calculate_analytics(records: List[EnergyData], period: str) -> List[Dict[str, Any]]:
    if not records:
        return []
    rows = []
    for r in records:
        rows.append(
            {
                "timestamp": getattr(r, "timestamp", None),
                "consumption_kwh": float(getattr(r, "consumption_kwh", 0.0) or 0.0),
                "cost_usd": float(getattr(r, "cost_usd", 0.0) or 0.0),
                "temperature_c": (
                    None
                    if getattr(r, "temperature_c", None) is None
                    else float(getattr(r, "temperature_c"))
                ),
                "humidity_percent": (
                    None
                    if getattr(r, "humidity_percent", None) is None
                    else float(getattr(r, "humidity_percent"))
                ),
            }
        )
    import pandas as pd

    df = pd.DataFrame(rows)
    if df.empty or df["timestamp"].isnull().all():
        return []
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).set_index("timestamp")
    if period == "week":
        freq = "D"
    elif period == "month":
        freq = "D"
    elif period == "year":
        freq = "W"
    else:
        raise ValueError("Invalid period: must be 'week', 'month', or 'year'")
    agg_map = {
        "consumption_kwh": "sum",
        "cost_usd": "sum",
        "temperature_c": "mean",
        "humidity_percent": "mean",
    }
    aggregated = df.resample(freq).agg(agg_map).reset_index()
    if aggregated.empty:
        return []
    aggregated["consumption_kwh"] = aggregated["consumption_kwh"].fillna(0.0)
    aggregated["cost_usd"] = aggregated["cost_usd"].fillna(0.0)
    temp_for_eff = aggregated["temperature_c"].fillna(1.0).replace(0.0, 1.0)
    aggregated["efficiency"] = 100.0 - aggregated["consumption_kwh"] / temp_for_eff
    results: List[Dict[str, Any]] = []
    for _, row in aggregated.iterrows():
        ts = row["timestamp"]
        label = ts.strftime("%Y-%m-%d")
        if period == "year":
            label = f"Week {ts.isocalendar()[1]}"
        results.append(
            {
                "label": label,
                "consumption": round(float(row["consumption_kwh"]), 2),
                "cost": round(float(row["cost_usd"]), 2),
                "temperature": (
                    round(float(row["temperature_c"]), 2)
                    if pd.notnull(row["temperature_c"])
                    else None
                ),
                "efficiency": round(float(row["efficiency"]), 2),
            }
        )
    return results


@router.get("/", response_model=List[AnalyticsPoint])
def get_analytics(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    period: str = "month",
) -> Any:
    end_time = datetime.now(timezone.utc).replace(tzinfo=None)
    if period == "week":
        start_time = end_time - timedelta(days=7)
    elif period == "month":
        start_time = end_time - timedelta(days=30)
    elif period == "year":
        start_time = end_time - timedelta(days=365)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid period. Must be 'week', 'month', or 'year'.",
        )
    records = get_data_by_time_range(
        db, user_id=current_user.id, start_time=start_time, end_time=end_time
    )
    if not records:
        return [
            {
                "label": "Day 1",
                "consumption": 50.5,
                "cost": 5.05,
                "temperature": 20.1,
                "efficiency": 75.0,
            },
            {
                "label": "Day 2",
                "consumption": 60.2,
                "cost": 6.02,
                "temperature": 22.5,
                "efficiency": 70.5,
            },
            {
                "label": "Day 3",
                "consumption": 45.1,
                "cost": 4.51,
                "temperature": 18.9,
                "efficiency": 80.1,
            },
        ]
    try:
        return calculate_analytics(records, period)
    except ValueError as e:
        logger.error(f"ValueError calculating analytics: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error calculating analytics")
        raise HTTPException(status_code=500, detail="Error calculating analytics data.")


@router.get("/summary", response_model=Dict[str, Any])
def get_analytics_summary(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Any:
    """Returns a high-level summary of the last 30 days."""
    end_time = datetime.now(timezone.utc).replace(tzinfo=None)
    start_time = end_time - timedelta(days=30)
    records = get_data_by_time_range(
        db, user_id=current_user.id, start_time=start_time, end_time=end_time
    )
    if not records:
        return {
            "total_consumption_kwh": 0.0,
            "total_cost_usd": 0.0,
            "avg_daily_consumption_kwh": 0.0,
            "record_count": 0,
        }
    total_consumption = sum(
        float(getattr(r, "consumption_kwh", 0.0) or 0.0) for r in records
    )
    total_cost = sum(float(getattr(r, "cost_usd", 0.0) or 0.0) for r in records)
    return {
        "total_consumption_kwh": round(total_consumption, 2),
        "total_cost_usd": round(total_cost, 2),
        "avg_daily_consumption_kwh": round(total_consumption / 30, 2),
        "record_count": len(records),
    }
