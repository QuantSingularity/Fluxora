from typing import Any, Dict, List, Tuple

import numpy as np
from core.config import get_config
from fastapi import FastAPI
from features.build_features import FeaturePipeline
from models.predict import get_model, predict_with_model

from .schemas import PredictionRequest, PredictionResponse

app = FastAPI(title="Fluxora API", description="Energy prediction API")

config = get_config()

feature_pipeline = FeaturePipeline()
_model = None


def get_cached_model() -> Any:
    """Lazy-load and cache the model."""
    global _model
    if _model is None:
        _model = get_model()
    return _model


from .health_check import router as health_router

app.include_router(health_router)


@app.post("/predict", response_model=PredictionResponse)
async def predict(payload: PredictionRequest) -> Dict[str, Any]:
    """
    Batch prediction endpoint
    """
    preprocessed = feature_pipeline.transform(payload)

    model = get_cached_model()
    predictions = predict_with_model(model, preprocessed)

    if predictions.ndim > 1 and predictions.shape[0] > 1:
        std_dev = np.std(predictions, axis=0)
    else:
        std_dev = float(np.std(predictions)) if len(predictions) > 1 else 1.0

    confidence_intervals: List[Tuple[float, float]] = [
        (float(pred - 1.96 * std_dev), float(pred + 1.96 * std_dev))
        for pred in predictions
    ]

    return {
        "predictions": predictions.tolist(),
        "confidence_intervals": confidence_intervals,
        "model_version": config.get("model_version", "0.1.0"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
