import logging
import os
from typing import Any

import tensorflow as tf
import xgboost as xgb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_latest_model(model_type: str) -> Any:
    """
    Loads the latest trained model based on the type.

    Args:
        model_type: The type of model to load ('xgboost' or 'lstm').

    Returns:
        The loaded model object.
    """
    model_dir = f"models/{model_type}/latest"
    if model_type == "xgboost":
        model_path = os.path.join(model_dir, "model.xgb")
        if not os.path.exists(model_path):
            logger.info(
                f"Warning: XGBoost model not found at {model_path}. Returning a mock model."
            )
            from .predict import MockModel

            return MockModel()
        model = xgb.Booster()
        model.load_model(model_path)
        return model
    elif model_type == "lstm":
        model_path = os.path.join(model_dir, "model")
        if not os.path.exists(model_path):
            logger.info(
                f"Warning: LSTM model not found at {model_path}. Returning a mock model."
            )
            from .predict import MockModel

            return MockModel()
        model = tf.keras.models.load_model(model_path)
        return model
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


if __name__ == "__main__":
    try:
        xgb_model = get_latest_model("xgboost")
        logger.info(f"Loaded XGBoost model: {xgb_model}")
    except Exception as e:
        logger.info(f"Error loading XGBoost model: {e}")
    try:
        lstm_model = get_latest_model("lstm")
        logger.info(f"Loaded LSTM model: {lstm_model}")
    except Exception as e:
        logger.info(f"Error loading LSTM model: {e}")
