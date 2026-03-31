from typing import Any

import numpy as np
from features.feature_store import get_feature_store


def get_model() -> Any:
    """
    Load the trained model from storage

    Returns:
        A mock model object for testing
    """
    return MockModel()


class MockModel:
    """Mock model class for testing"""

    def predict(self, features: Any) -> Any:
        """Generate random predictions"""
        if isinstance(features, dict):
            num_samples = len(next(iter(features.values())))
        elif hasattr(features, "shape"):
            num_samples = features.shape[0]
        else:
            num_samples = len(features)
        return np.random.uniform(10, 100, size=num_samples)


def predict_with_model(model: Any, features: Any) -> Any:
    """
    Make predictions using the loaded model

    Args:
        model: The trained model object
        features: Preprocessed features

    Returns:
        numpy array of predictions
    """
    predictions = model.predict(features)
    return np.array(predictions)


def predict_energy_consumption(request_data: Any) -> Any:
    """
    Predict energy consumption based on input data

    Args:
        request_data: Input data from API request

    Returns:
        Predictions, timestamps, and confidence intervals
    """
    timestamps = request_data.timestamps
    meter_ids = request_data.meter_ids
    context_features = request_data.context_features or {}
    feature_store = get_feature_store()
    entity_rows = [{"meter_id": meter_id} for meter_id in meter_ids]
    features = feature_store.get_online_features(
        entity_rows=entity_rows,
        features=[
            "hourly_energy_features:lag_24h",
            "hourly_energy_features:rolling_7d_mean",
            "hourly_energy_features:temperature",
        ],
    )
    for key, values in context_features.items():
        if isinstance(values, list) and len(values) > 0:
            features[key] = values
    model = get_model()
    predictions = predict_with_model(model, features)
    std_dev = np.std(predictions) * 0.5
    confidence_intervals = [
        (float(pred - 1.96 * std_dev), float(pred + 1.96 * std_dev))
        for pred in predictions
    ]
    return {
        "predictions": predictions.tolist(),
        "timestamps": timestamps,
        "confidence_intervals": confidence_intervals,
        "model_version": "0.1.0-test",
    }
