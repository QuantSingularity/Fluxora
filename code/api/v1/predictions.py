from typing import Annotated, List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import joblib
import os
import pandas as pd
import numpy as np
from backend.dependencies import get_db
from backend.security import get_current_active_user
from schemas.user import User
from data.features.feature_engineering import preprocess_data_for_model
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predictions", tags=["predictions"])
MODEL_PATH = os.path.join(os.getcwd(), "fluxora_model.joblib")


def load_model() -> Any:
    """Loads the trained model from disk."""
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        logger.info(f"Error loading model: {e}")
        return None


def generate_mock_predictions(days: int) -> List[Dict[str, Any]]:
    """Generates mock prediction data."""
    data = []
    now = datetime.utcnow()
    for i in range(days * 24):
        timestamp = now + timedelta(hours=i)
        hour = timestamp.hour
        base_load = 50
        daily_cycle = np.sin(hour / 24 * 2 * np.pi) * 20
        noise = np.random.normal(0, 5)
        predicted = base_load + daily_cycle + noise
        data.append(
            {
                "timestamp": timestamp.isoformat(),
                "predicted_consumption": round(predicted, 2),
                "confidence_interval": {
                    "lower": round(predicted * 0.85, 2),
                    "upper": round(predicted * 1.15, 2),
                },
            }
        )
    return data


@router.get("/", response_model=List[Dict[str, Any]])
def get_predictions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    days: int = 7,
) -> Any:
    """
    Generates energy consumption predictions for the next 'days' ahead.
    """
    model = load_model()
    if model is None:
        return generate_mock_predictions(days)
    from crud.data import get_data_records

    historical_records = get_data_records(db, user_id=current_user.id, limit=48)
    if not historical_records:
        return generate_mock_predictions(days)
    historical_df = pd.DataFrame([r.__dict__ for r in historical_records])
    historical_df["timestamp"] = pd.to_datetime(historical_df["timestamp"])
    historical_df = historical_df.sort_values("timestamp")
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
    for i in range(start_idx, len(full_df)):
        temp_df = preprocess_data_for_model(full_df.iloc[:i].copy())
        current_features = temp_df.iloc[-1]
        target_col = "consumption_kwh"
        features = [
            col
            for col in temp_df.columns
            if col not in [target_col, "timestamp", "user_id"]
        ]
        X_pred = current_features[features].to_frame().T
        prediction = model.predict(X_pred)[0]
        full_df.loc[i, "consumption_kwh"] = prediction
    predictions_df = full_df.iloc[start_idx:].copy()
    results = []
    for _, row in predictions_df.iterrows():
        predicted = row["consumption_kwh"]
        results.append(
            {
                "timestamp": row["timestamp"].isoformat(),
                "predicted_consumption": round(predicted, 2),
                "confidence_interval": {
                    "lower": round(predicted * 0.9, 2),
                    "upper": round(predicted * 1.1, 2),
                },
            }
        )
    return results
