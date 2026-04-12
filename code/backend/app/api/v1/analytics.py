import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Dict, List, Optional

import pandas as pd
from app.core.security import get_current_active_user
from app.crud.data import get_data_by_time_range
from app.db.dependencies import get_db
from app.models.data import EnergyData
from app.schemas.user import User
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsPoint(BaseModel):
    label: str
    consumption: float
    cost: float
    temperature: Optional[float] = None
    efficiency: float


def _compute_efficiency(consumption: pd.Series, temperature: pd.Series) -> pd.Series:
    """
    Compute a normalised efficiency score in [0, 100].

    Formula: efficiency = 100 * (1 - consumption / (consumption.max() + ε))
    This gives 100 when consumption is 0 and approaches 0 as consumption
    approaches the observed maximum.  Temperature is intentionally excluded
    because dividing consumption by temperature produces physically
    meaningless results when temperature is near zero or negative.

    Bug fix: the original formula ``100 - consumption / temp`` produced
    values far outside [0, 100] whenever temperature was small, and the
    direction was wrong (higher temperature → lower divisor → lower
    efficiency score even for the same consumption).
    """
    max_consumption = consumption.max()
    if max_consumption == 0:
        return pd.Series(100.0, index=consumption.index)
    efficiency = 100.0 * (1.0 - consumption / (max_consumption + 1e-9))
    return efficiency.clip(lower=0.0, upper=100.0)


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
                    else float(r.temperature_c)  # type: ignore[arg-type]
                ),
                "humidity_percent": (
                    None
                    if getattr(r, "humidity_percent", None) is None
                    else float(r.humidity_percent)  # type: ignore[arg-type]
                ),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty or df["timestamp"].isnull().all():
        return []

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
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

    # Fixed efficiency: normalised relative to the period's maximum consumption
    aggregated["efficiency"] = _compute_efficiency(
        aggregated["consumption_kwh"], aggregated["temperature_c"]
    )

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


_MOCK_ANALYTICS = [
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


@router.get("/", response_model=List[AnalyticsPoint])
def get_analytics(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    period: str = Query(default="month", pattern="^(week|month|year)$"),
) -> Any:
    """Return aggregated energy analytics for the current user."""
    now = datetime.now(timezone.utc)
    if period == "week":
        start_time = now - timedelta(days=7)
    elif period == "month":
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(days=365)

    start_naive = start_time.replace(tzinfo=None)
    end_naive = now.replace(tzinfo=None)

    records = get_data_by_time_range(
        db, user_id=current_user.id, start_time=start_naive, end_time=end_naive
    )
    if not records:
        return _MOCK_ANALYTICS

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
    """Return a high-level summary of the last 30 days."""
    now = datetime.now(timezone.utc)
    end_naive = now.replace(tzinfo=None)
    start_naive = (now - timedelta(days=30)).replace(tzinfo=None)

    records = get_data_by_time_range(
        db, user_id=current_user.id, start_time=start_naive, end_time=end_naive
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
    days_span = max((end_naive - start_naive).days, 1)
    return {
        "total_consumption_kwh": round(total_consumption, 2),
        "total_cost_usd": round(total_cost, 2),
        "avg_daily_consumption_kwh": round(total_consumption / days_span, 2),
        "record_count": len(records),
    }
