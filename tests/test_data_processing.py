"""
Tests for data processing functionality.
"""

import numpy as np
import pandas as pd
import pytest
from typing import Any
from code.data.processing import (
    extract_features,
    handle_missing_values,
    normalize_features,
    preprocess_data,
)


@pytest.fixture
def sample_data() -> Any:
    """Create sample data for testing."""
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="H"),
            "temperature": [
                20.5,
                21.0,
                np.nan,
                22.0,
                21.5,
                20.0,
                19.5,
                20.0,
                21.0,
                22.0,
            ],
            "humidity": [60, 62, 65, 63, 61, 59, 58, 60, 62, 64],
            "power_consumption": [100, 105, 110, 108, 102, 98, 95, 100, 105, 110],
        }
    )


@pytest.fixture
def empty_data() -> Any:
    """Create empty DataFrame for testing."""
    return pd.DataFrame(
        columns=["timestamp", "temperature", "humidity", "power_consumption"]
    )


@pytest.fixture
def all_missing_data() -> Any:
    """Create DataFrame with all missing values."""
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2024-01-01", periods=5, freq="H"),
            "temperature": [np.nan] * 5,
            "humidity": [np.nan] * 5,
            "power_consumption": [np.nan] * 5,
        }
    )


def test_preprocess_data(sample_data: Any) -> Any:
    """Test data preprocessing function."""
    processed_data = preprocess_data(sample_data)
    assert isinstance(processed_data, pd.DataFrame)
    assert not processed_data.isnull().any().any()
    assert "hour" in processed_data.columns
    assert "day_of_week" in processed_data.columns


def test_preprocess_empty_data(empty_data: Any) -> Any:
    """Test preprocessing with empty DataFrame."""
    with pytest.raises(ValueError, match="Empty DataFrame"):
        preprocess_data(empty_data)


def test_normalize_features(sample_data: Any) -> Any:
    """Test feature normalization."""
    normalized_data = normalize_features(
        sample_data[["temperature", "humidity", "power_consumption"]]
    )
    assert isinstance(normalized_data, pd.DataFrame)
    assert normalized_data.shape == (10, 3)
    assert normalized_data.min().min() >= 0
    assert normalized_data.max().max() <= 1


def test_normalize_features_with_constant_column() -> Any:
    """Test normalization with constant column."""
    constant_data = pd.DataFrame({"constant": [1] * 10, "varying": range(10)})
    normalized_data = normalize_features(constant_data)
    assert normalized_data["constant"].nunique() == 1
    assert normalized_data["varying"].nunique() == 10


def test_handle_missing_values(sample_data: Any) -> Any:
    """Test missing value handling."""
    processed_data = handle_missing_values(sample_data)
    assert isinstance(processed_data, pd.DataFrame)
    assert not processed_data.isnull().any().any()
    assert processed_data.shape == (10, 4)


def test_handle_all_missing_values(all_missing_data: Any) -> Any:
    """Test handling of all missing values."""
    with pytest.raises(ValueError, match="All values are missing"):
        handle_missing_values(all_missing_data)


def test_extract_features(sample_data: Any) -> Any:
    """Test feature extraction."""
    features = extract_features(sample_data)
    assert isinstance(features, pd.DataFrame)
    assert "rolling_mean_24h" in features.columns
    assert "rolling_std_24h" in features.columns
    assert "lag_1" in features.columns


def test_extract_features_with_insufficient_data() -> Any:
    """Test feature extraction with insufficient data."""
    small_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2024-01-01", periods=2, freq="H"),
            "temperature": [20.5, 21.0],
            "humidity": [60, 62],
            "power_consumption": [100, 105],
        }
    )
    with pytest.raises(ValueError, match="Insufficient data points"):
        extract_features(small_data)


@pytest.mark.integration
def test_end_to_end_processing(sample_data: Any) -> Any:
    """Test the entire data processing pipeline."""
    processed_data = preprocess_data(sample_data)
    clean_data = handle_missing_values(processed_data)
    features = extract_features(clean_data)
    normalized_features = normalize_features(features)
    assert isinstance(normalized_features, pd.DataFrame)
    assert not normalized_features.isnull().any().any()
    assert normalized_features.shape[0] == 10


@pytest.mark.integration
def test_end_to_end_processing_with_edge_cases() -> Any:
    """Test the entire pipeline with edge cases."""
    edge_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2024-01-01", periods=15, freq="H"),
            "temperature": [20.5] + [np.nan] * 13 + [22.0],
            "humidity": [60] * 15,
            "power_consumption": [100] + [np.nan] * 13 + [110],
        }
    )
    processed_data = preprocess_data(edge_data)
    clean_data = handle_missing_values(processed_data)
    features = extract_features(clean_data)
    normalized_features = normalize_features(features)
    assert isinstance(normalized_features, pd.DataFrame)
    assert not normalized_features.isnull().any().any()
    assert normalized_features.shape[0] == 15
