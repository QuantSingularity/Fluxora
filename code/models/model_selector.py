import logging
import os
from typing import Any

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
        model_type: The type of model to load ('xgboost', 'random_forest', or 'lstm').

    Returns:
        The loaded model object, or a MockModel if no saved model is found.
    """
    from models.predict import MockModel

    if model_type == "xgboost":
        model_dir = f"models/{model_type}/latest"
        model_path = os.path.join(model_dir, "model.xgb")
        if not os.path.exists(model_path):
            logger.warning(
                f"XGBoost model not found at {model_path}. Returning a mock model."
            )
            return MockModel()
        model = xgb.Booster()
        model.load_model(model_path)
        return model

    elif model_type == "random_forest":
        import joblib

        model_path = os.path.join("fluxora_model.joblib")
        if not os.path.exists(model_path):
            logger.warning(
                f"RandomForest model not found at {model_path}. Returning a mock model."
            )
            return MockModel()
        return joblib.load(model_path)

    elif model_type == "lstm":
        try:
            import tensorflow as tf
        except ImportError:
            logger.warning("TensorFlow not installed. Returning a mock model.")
            return MockModel()
        model_dir = f"models/{model_type}/latest"
        model_path = os.path.join(model_dir, "model")
        if not os.path.exists(model_path):
            logger.warning(
                f"LSTM model not found at {model_path}. Returning a mock model."
            )
            return MockModel()
        return tf.keras.models.load_model(model_path)

    else:
        raise ValueError(
            f"Unsupported model type: {model_type}. Choose from: xgboost, random_forest, lstm"
        )


if __name__ == "__main__":
    for mtype in ["xgboost", "random_forest"]:
        try:
            m = get_latest_model(mtype)
            logger.info(f"Loaded {mtype} model: {m}")
        except Exception as e:
            logger.error(f"Error loading {mtype} model: {e}")
