import logging
import os
from datetime import datetime, timedelta
from typing import Any, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.getcwd(), "fluxora_model.joblib")


def load_data_from_db(db_session: Any = None) -> pd.DataFrame:
    """
    Loads all energy data from the database.
    Falls back to synthetic data when no session is provided or DB is empty.
    """
    if db_session is not None:
        try:
            from app.models.data import EnergyData

            records = db_session.query(EnergyData).order_by(EnergyData.timestamp).all()
            if records:
                rows = [
                    {
                        "timestamp": r.timestamp,
                        "consumption_kwh": float(r.consumption_kwh),
                        "user_id": r.user_id,
                    }
                    for r in records
                ]
                return pd.DataFrame(rows)
        except Exception as e:
            logger.warning(f"Could not load data from DB, using synthetic: {e}")

    start_time = datetime.now() - timedelta(days=30)
    timestamps = [start_time + timedelta(hours=i) for i in range(30 * 24)]
    time_series_index = np.arange(len(timestamps))
    daily_cycle = np.sin(time_series_index * 2 * np.pi / 24) * 10
    weekly_cycle = np.sin(time_series_index * 2 * np.pi / (24 * 7)) * 20
    base_load = 50
    noise = np.random.normal(0, 5, len(timestamps))
    consumption = np.abs(base_load + daily_cycle + weekly_cycle + noise)
    return pd.DataFrame(
        {"timestamp": timestamps, "consumption_kwh": consumption, "user_id": 1}
    )


def train_model(df: pd.DataFrame) -> Tuple[RandomForestRegressor, dict]:
    """Trains a RandomForestRegressor on the processed data."""
    from app.services.feature_engineering import preprocess_data_for_model

    processed_df = preprocess_data_for_model(df.copy())
    target_col = "consumption_kwh"
    features = [
        col
        for col in processed_df.columns
        if col not in [target_col, "timestamp", "user_id"]
    ]
    X = processed_df[features]
    y = processed_df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = float(mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))
    metrics = {
        "mean_squared_error": mse,
        "r2_score": r2,
        "feature_count": len(features),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }
    logger.info(f"Model Training Complete. MSE: {mse:.4f}, R2: {r2:.4f}")
    return (model, metrics)


def save_model(model: RandomForestRegressor, path: str = "") -> None:
    """Saves the trained model to disk."""
    if not path:
        path = MODEL_PATH
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    joblib.dump(model, path)
    logger.info(f"Model saved to {path}")


def run_training_pipeline(db_session: Any = None, model_path: str = "") -> dict:
    """Full pipeline: load data → train model → save."""
    logger.info("Starting training pipeline...")
    data_df = load_data_from_db(db_session)
    model, metrics = train_model(data_df)
    save_model(model, path=model_path or MODEL_PATH)
    return metrics
