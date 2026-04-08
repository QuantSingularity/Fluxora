import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Dict, List

import numpy as np
import pandas as pd
from app.core.security import get_current_active_user
from app.db.dependencies import get_db
from app.schemas.user import User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

try:
    import joblib

    _JOBLIB_AVAILABLE = True
except ImportError:
    _JOBLIB_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["predictions"])
MODEL_PATH = os.path.join(os.getcwd(), "fluxora_model.joblib")


def load_model() -> Any:
    """Load the trained model from disk, returning None if unavailable."""
    if not _JOBLIB_AVAILABLE:
        return None
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None


def generate_mock_predictions(days: int) -> List[Dict[str, Any]]:
    """Generate mock prediction data when no trained model is available."""
    data = []
    now = datetime.now(timezone.utc)
    for i in range(days * 24):
        timestamp = now + timedelta(hours=i)
        hour = timestamp.hour
        base_load = 50.0
        daily_cycle = np.sin(hour / 24 * 2 * np.pi) * 20
        noise = np.random.normal(0, 5)
        predicted = float(base_load + daily_cycle + noise)
        margin = abs(predicted) * 0.15
        data.append(
            {
                "timestamp": timestamp.isoformat(),
                "predicted_consumption": round(predicted, 2),
                "confidence_interval": {
                    "lower": round(predicted - margin, 2),
                    "upper": round(predicted + margin, 2),
                },
            }
        )
    return data


@router.get("/", response_model=List[Dict[str, Any]])
def get_predictions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    days: int = Query(default=7, ge=1, le=90),
) -> Any:
    """
    Generate energy consumption predictions for the next N days.
    Falls back to mock predictions when no trained model or historical data is available.
    """
    model = load_model()
    if model is None:
        logger.info("No trained model found. Returning mock predictions.")
        return generate_mock_predictions(days)

    from app.crud.data import get_data_records

    historical_records = get_data_records(db, user_id=current_user.id, limit=48)
    if not historical_records:
        logger.info("No historical records found. Returning mock predictions.")
        return generate_mock_predictions(days)

    historical_df = pd.DataFrame(
        [
            {
                "timestamp": r.timestamp,
                "consumption_kwh": float(r.consumption_kwh),
                "user_id": r.user_id,
            }
            for r in historical_records
        ]
    )

    if historical_df.empty:
        return generate_mock_predictions(days)

    historical_df["timestamp"] = pd.to_datetime(historical_df["timestamp"])
    historical_df = historical_df.sort_values("timestamp").reset_index(drop=True)

    future_timestamps = [
        historical_df["timestamp"].iloc[-1] + timedelta(hours=i)
        for i in range(1, days * 24 + 1)
    ]
    future_df = pd.DataFrame(
        {
            "timestamp": future_timestamps,
            "consumption_kwh": np.nan,
            "user_id": current_user.id,
        }
    )
    full_df = pd.concat([historical_df, future_df], ignore_index=True)
    start_idx = len(historical_df)

    from app.services.feature_engineering import preprocess_data_for_model

    for i in range(start_idx, len(full_df)):
        temp_df = preprocess_data_for_model(full_df.iloc[:i].copy())
        if temp_df.empty:
            full_df.loc[i, "consumption_kwh"] = historical_df["consumption_kwh"].mean()
            continue

        target_col = "consumption_kwh"
        features = [
            col
            for col in temp_df.columns
            if col not in [target_col, "timestamp", "user_id"]
        ]
        X_pred = temp_df[features].iloc[[-1]]
        prediction = float(model.predict(X_pred)[0])
        full_df.loc[i, "consumption_kwh"] = max(prediction, 0.0)

    predictions_df = full_df.iloc[start_idx:].copy()
    results = []
    for _, row in predictions_df.iterrows():
        predicted = float(row["consumption_kwh"])
        margin = abs(predicted) * 0.10
        results.append(
            {
                "timestamp": row["timestamp"].isoformat(),
                "predicted_consumption": round(predicted, 2),
                "confidence_interval": {
                    "lower": round(predicted - margin, 2),
                    "upper": round(predicted + margin, 2),
                },
            }
        )
    return results


@router.post("/train", response_model=Dict[str, Any])
def trigger_training(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Any:
    """
    Trigger model (re-)training using data from the database.
    Restricted to superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can trigger training.",
        )
    from app.services.training import run_training_pipeline

    metrics = run_training_pipeline(db_session=db)
    return {"status": "trained", "metrics": metrics}
