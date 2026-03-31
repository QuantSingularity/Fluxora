from typing import Any

"""
Unit tests for the model training logic.
"""

from code.models.train import (
    objective,
    prepare_training_data,
    train_lstm_model,
    train_model,
    train_xgboost_model,
)
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_data() -> Any:
    """Create sample data for model training tests."""
    np.random.seed(42)
    n_samples = 100
    data = pd.DataFrame(
        {
            "feature1": np.random.normal(0, 1, n_samples),
            "feature2": np.random.normal(0, 1, n_samples),
            "feature3": np.random.normal(0, 1, n_samples),
            "target": np.random.normal(0, 1, n_samples),
        }
    )
    return data


@pytest.fixture
def prepared_data(sample_data: Any) -> Any:
    """Create prepared training and validation data."""
    X = sample_data[["feature1", "feature2", "feature3"]].values
    y = sample_data["target"].values
    split_idx = int(len(X) * 0.8)
    X_train, X_val = (X[:split_idx], X[split_idx:])
    y_train, y_val = (y[:split_idx], y[split_idx:])
    return (X_train, X_val, y_train, y_val)


@patch("src.models.train.load_data")
def test_prepare_training_data(mock_load_data: Any, sample_data: Any) -> Any:
    """Test data preparation for training."""
    mock_load_data.return_value = sample_data
    X_train, X_val, y_train, y_val = prepare_training_data(sample_data)
    assert X_train.shape[1] == 3
    assert X_val.shape[1] == 3
    assert len(y_train.shape) == 1
    assert len(y_val.shape) == 1
    assert X_train.shape[0] > X_val.shape[0]
    assert y_train.shape[0] == X_train.shape[0]
    assert y_val.shape[0] == X_val.shape[0]


@patch("src.models.train.xgb")
def test_train_xgboost_model(mock_xgb: Any, prepared_data: Any) -> Any:
    """Test XGBoost model training."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_model = MagicMock()
    mock_xgb.train.return_value = mock_model
    params = {
        "learning_rate": 0.1,
        "n_estimators": 100,
        "max_depth": 5,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 1,
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
    }
    model = train_xgboost_model(X_train, y_train, X_val, y_val, params)
    assert mock_xgb.DMatrix.call_count == 2
    assert mock_xgb.train.call_count == 1
    assert model == mock_model


@patch("src.models.train.Sequential")
@patch("src.models.train.LSTM")
@patch("src.models.train.Dense")
@patch("src.models.train.Dropout")
def test_train_lstm_model(
    mock_dropout: Any,
    mock_dense: Any,
    mock_lstm: Any,
    mock_sequential: Any,
    prepared_data: Any,
) -> Any:
    """Test LSTM model training."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_model = MagicMock()
    mock_sequential.return_value = mock_model
    params = {"units": 50, "dropout": 0.2, "batch_size": 32, "epochs": 10}
    model = train_lstm_model(X_train, y_train, X_val, y_val, params)
    assert mock_sequential.call_count == 1
    assert mock_lstm.call_count == 1
    assert mock_dropout.call_count == 1
    assert mock_dense.call_count == 1
    assert mock_model.compile.call_count == 1
    assert mock_model.fit.call_count == 1
    assert model == mock_model


@patch("src.models.train.load_data")
@patch("src.models.train.prepare_training_data")
@patch("src.models.train.get_config")
@patch("src.models.train.xgb")
def test_objective_xgboost(
    mock_xgb: Any,
    mock_get_config: Any,
    mock_prepare_data: Any,
    mock_load_data: Any,
    prepared_data: Any,
    sample_data: Any,
) -> Any:
    """Test objective function with XGBoost model."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_load_data.return_value = sample_data
    mock_prepare_data.return_value = (X_train, X_val, y_train, y_val)
    mock_get_config.return_value = {"model": {"type": "xgboost"}}
    mock_model = MagicMock()
    mock_model.predict.return_value = y_val
    mock_xgb.train.return_value = mock_model
    mock_trial = MagicMock()
    mock_trial.suggest_float.return_value = 0.1
    mock_trial.suggest_int.return_value = 5
    rmse = objective(mock_trial)
    assert isinstance(rmse, float)
    assert mock_trial.suggest_float.call_count >= 3
    assert mock_trial.suggest_int.call_count >= 3


@patch("src.models.train.load_data")
@patch("src.models.train.prepare_training_data")
@patch("src.models.train.get_config")
@patch("src.models.train.Sequential")
def test_objective_lstm(
    mock_sequential: Any,
    mock_get_config: Any,
    mock_prepare_data: Any,
    mock_load_data: Any,
    prepared_data: Any,
    sample_data: Any,
) -> Any:
    """Test objective function with LSTM model."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_load_data.return_value = sample_data
    mock_prepare_data.return_value = (X_train, X_val, y_train, y_val)
    mock_get_config.return_value = {"model": {"type": "lstm"}}
    mock_model = MagicMock()
    mock_model.predict.return_value = np.expand_dims(y_val, axis=1)
    mock_sequential.return_value = mock_model
    mock_trial = MagicMock()
    mock_trial.suggest_int.return_value = 64
    mock_trial.suggest_float.return_value = 0.3
    rmse = objective(mock_trial)
    assert isinstance(rmse, float)
    assert mock_trial.suggest_int.call_count >= 2
    assert mock_trial.suggest_float.call_count >= 1


@patch("src.models.train.mlflow")
@patch("src.models.train.optuna")
@patch("src.models.train.load_data")
@patch("src.models.train.prepare_training_data")
@patch("src.models.train.get_config")
@patch("src.models.train.train_xgboost_model")
@patch("src.models.train.os.makedirs")
def test_train_model_xgboost(
    mock_makedirs: Any,
    mock_train_xgb: Any,
    mock_get_config: Any,
    mock_prepare_data: Any,
    mock_load_data: Any,
    mock_optuna: Any,
    mock_mlflow: Any,
    prepared_data: Any,
    sample_data: Any,
) -> Any:
    """Test full model training pipeline with XGBoost."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_load_data.return_value = sample_data
    mock_prepare_data.return_value = (X_train, X_val, y_train, y_val)
    mock_get_config.return_value = {"model": {"type": "xgboost"}}
    mock_study = MagicMock()
    mock_study.best_params = {
        "learning_rate": 0.05,
        "n_estimators": 200,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 3,
    }
    mock_optuna.create_study.return_value = mock_study
    mock_model = MagicMock()
    mock_train_xgb.return_value = mock_model
    model = train_model()
    assert mock_mlflow.start_run.call_count == 1
    assert mock_mlflow.log_param.call_count >= 1
    assert mock_mlflow.end_run.call_count == 1
    assert mock_train_xgb.call_count == 1
    assert mock_model.save_model.call_count == 1
    assert model == mock_model


@patch("src.models.train.mlflow")
@patch("src.models.train.optuna")
@patch("src.models.train.load_data")
@patch("src.models.train.prepare_training_data")
@patch("src.models.train.get_config")
@patch("src.models.train.train_lstm_model")
@patch("src.models.train.os.makedirs")
def test_train_model_lstm(
    mock_makedirs: Any,
    mock_train_lstm: Any,
    mock_get_config: Any,
    mock_prepare_data: Any,
    mock_load_data: Any,
    mock_optuna: Any,
    mock_mlflow: Any,
    prepared_data: Any,
    sample_data: Any,
) -> Any:
    """Test full model training pipeline with LSTM."""
    X_train, X_val, y_train, y_val = prepared_data
    mock_load_data.return_value = sample_data
    mock_prepare_data.return_value = (X_train, X_val, y_train, y_val)
    mock_get_config.return_value = {"model": {"type": "lstm"}}
    mock_study = MagicMock()
    mock_study.best_params = {"units": 128, "dropout": 0.3, "batch_size": 64}
    mock_optuna.create_study.return_value = mock_study
    mock_model = MagicMock()
    mock_train_lstm.return_value = mock_model
    model = train_model()
    assert mock_mlflow.start_run.call_count == 1
    assert mock_mlflow.log_param.call_count >= 1
    assert mock_mlflow.end_run.call_count == 1
    assert mock_train_lstm.call_count == 1
    assert mock_model.save.call_count == 1
    assert model == mock_model


def test_invalid_model_type() -> Any:
    """Test handling of invalid model type."""
    with patch("src.models.train.get_config") as mock_get_config:
        mock_get_config.return_value = {"model": {"type": "invalid_model"}}
        mock_trial = MagicMock()
        with pytest.raises(ValueError, match="Unsupported model type"):
            objective(mock_trial)
