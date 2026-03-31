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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.getcwd(), "fluxora_model.joblib")


def load_data_from_db(db_session: Any = None) -> pd.DataFrame:
    """
    Loads all energy data from the database into a pandas DataFrame.

    NOTE: In a real application, this would query the database.
    For now, we'll create dummy data for demonstration.
    """
    start_time = datetime.now() - timedelta(days=30)
    timestamps = [start_time + timedelta(hours=i) for i in range(30 * 24)]
    time_series_index = np.arange(len(timestamps))
    daily_cycle = np.sin(time_series_index * 2 * np.pi / 24) * 10
    weekly_cycle = np.sin(time_series_index * 2 * np.pi / (24 * 7)) * 20
    base_load = 50
    noise = np.random.normal(0, 5, len(timestamps))
    consumption = np.abs(base_load + daily_cycle + weekly_cycle + noise)
    df = pd.DataFrame(
        {"timestamp": timestamps, "consumption_kwh": consumption, "user_id": 1}
    )
    return df


def train_model(df: pd.DataFrame) -> Tuple[RandomForestRegressor, dict]:
    """
    Trains a RandomForestRegressor model on the processed data.

    Args:
        df: Raw DataFrame containing the time-series data.

    Returns:
        A tuple containing the trained model and a dictionary of evaluation metrics.
    """
    from ..data.features.feature_engineering import preprocess_data_for_model

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
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    metrics = {
        "mean_squared_error": mse,
        "r2_score": r2,
        "feature_count": len(features),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }
    logger.info(f"Model Training Complete. MSE: {mse:.4f}, R2: {r2:.4f}")
    return (model, metrics)


def save_model(model: RandomForestRegressor, path: str = MODEL_PATH) -> Any:
    """Saves the trained model to a file."""
    joblib.dump(model, path)
    logger.info(f"Model saved to {path}")


def run_training_pipeline(db_session: Any = None) -> Any:
    """Full pipeline to load data, train model, and save it."""
    logger.info("Starting training pipeline...")
    data_df = load_data_from_db(db_session)
    model, metrics = train_model(data_df)
    save_model(model)
    return metrics


if __name__ == "__main__":
    metrics = run_training_pipeline()
    logger.info("\nFinal Metrics:")
    logger.info(metrics)
