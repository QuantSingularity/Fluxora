"""
Hyperparameter tuning script using Optuna and MLflow.
Run this script directly to tune the XGBoost model.
"""

import logging
from typing import Any

import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_hyperparameter_tuning(n_trials: int = 100, timeout: int = 3600) -> dict:
    """
    Runs Optuna hyperparameter search with optional MLflow tracking.

    Args:
        n_trials: Number of Optuna trials.
        timeout: Maximum search time in seconds.

    Returns:
        dict with best_params and best_value.
    """
    try:
        import mlflow

        mlflow_available = True
    except ImportError:
        logger.warning("MLflow not installed; running without experiment tracking.")
        mlflow_available = False

    try:
        import optuna
    except ImportError:
        raise ImportError(
            "optuna is required for hyperparameter tuning. "
            "Install with: pip install optuna"
        )

    from data.features.feature_engineering import preprocess_data_for_model
    from models.train import load_data_from_db

    logger.info("Loading and preparing training data...")
    raw_df = load_data_from_db()
    processed_df = preprocess_data_for_model(raw_df.copy())

    target_col = "consumption_kwh"
    feature_cols = [
        col
        for col in processed_df.columns
        if col not in [target_col, "timestamp", "user_id"]
    ]
    X = processed_df[feature_cols].values
    y = processed_df[target_col].values

    def objective(trial: Any) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "learning_rate": trial.suggest_float(
                "learning_rate", 0.0001, 0.3, log=True
            ),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        }
        context = mlflow.start_run(nested=True) if mlflow_available else None
        try:
            model = xgb.XGBRegressor(**params, random_state=42)
            cv = TimeSeriesSplit(n_splits=5)
            scores = []
            for fold, (train_idx, val_idx) in enumerate(cv.split(X)):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
                preds = model.predict(X_val)
                score = mean_absolute_error(y_val, preds)
                if mlflow_available:
                    mlflow.log_metric(f"fold_{fold}_mae", score)
                scores.append(score)

            avg_score = float(np.mean(scores))
            trial.report(avg_score, step=1)
            if trial.should_prune():
                raise optuna.TrialPruned()

            if mlflow_available:
                mlflow.log_params(params)
                mlflow.log_metric("avg_mae", avg_score)

            return avg_score
        finally:
            if context is not None:
                context.__exit__(None, None, None)

    study = optuna.create_study(
        direction="minimize",
        pruner=optuna.pruners.MedianPruner(),
    )
    study.optimize(objective, n_trials=n_trials, timeout=timeout)

    best = {"best_params": study.best_params, "best_value": study.best_value}
    logger.info(f"Best params: {study.best_params}")
    logger.info(f"Best MAE: {study.best_value:.4f}")

    if mlflow_available:
        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_mae", study.best_value)

    return best


if __name__ == "__main__":
    result = run_hyperparameter_tuning(n_trials=50, timeout=1800)
    logger.info(result)
