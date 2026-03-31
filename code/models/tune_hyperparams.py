from code.models.train import load_data, prepare_training_data
from typing import Any

import mlflow
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error

data = load_data()
X, _, y, _ = prepare_training_data(data)
import optuna
from sklearn.model_selection import TimeSeriesSplit


def objective(trial: Any) -> Any:
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 0.0001, 0.3, log=True),
    }
    with mlflow.start_run(nested=True):
        model = xgb.XGBRegressor(**params)
        cv = TimeSeriesSplit(n_splits=5)
        scores = []
        for fold, (train_idx, val_idx) in enumerate(cv.split(X)):
            X_train, X_val = (X[train_idx], X[val_idx])
            y_train, y_val = (y[train_idx], y[val_idx])
            model.fit(X_train, y_train)
            preds = model.predict(X_val)
            score = mean_absolute_error(y_val, preds)
            mlflow.log_metric(f"fold_{fold}_mae", score)
            scores.append(score)
        avg_score = np.mean(scores)
        trial.report(avg_score, step=1)
        if trial.should_prune():
            raise optuna.TrialPruned()
        return avg_score


study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=100, timeout=3600)
mlflow.log_params(study.best_params)
