"""
Unit tests for the feature store implementation.
"""

from code.data.feature_store import FeatureStoreClient
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import pytest


@pytest.fixture
def feature_store() -> Any:
    """Create a clean feature store for testing."""
    fs = FeatureStoreClient()
    for view in fs.list_feature_views():
        fs.delete_feature_view(view)
    return fs


@pytest.fixture
def sample_feature_view(feature_store: Any) -> Any:
    """Create a sample feature view with test data."""
    feature_store.register_feature_view(
        feature_view_name="test_features",
        entity_keys=["user_id"],
        features=["avg_transaction_value", "transaction_count"],
    )
    return feature_store


@pytest.fixture
def sample_features() -> Any:
    """Sample feature data for testing."""
    return {"avg_transaction_value": 150.75, "transaction_count": 5}


def test_register_feature_view(feature_store: Any) -> Any:
    """Test registering a new feature view."""
    feature_store.register_feature_view(
        feature_view_name="energy_features",
        entity_keys=["device_id"],
        features=["power_consumption", "voltage", "current"],
    )
    feature_views = feature_store.list_feature_views()
    assert "energy_features" in feature_views
    metadata = feature_store.get_feature_view_metadata("energy_features")
    assert metadata["entity_keys"] == ["device_id"]
    assert set(metadata["features"]) == {"power_consumption", "voltage", "current"}


def test_push_and_get_online_features(
    sample_feature_view: Any, sample_features: Any
) -> Any:
    """Test pushing features and retrieving them."""
    sample_feature_view.push_features("test_features", "user123", sample_features)
    retrieved_features = sample_feature_view.get_online_features(
        "test_features", "user123"
    )
    assert (
        retrieved_features["avg_transaction_value"]
        == sample_features["avg_transaction_value"]
    )
    assert (
        retrieved_features["transaction_count"] == sample_features["transaction_count"]
    )


def test_push_features_with_timestamp(
    sample_feature_view: Any, sample_features: Any
) -> Any:
    """Test pushing features with timestamps."""
    timestamp1 = datetime.now() - timedelta(hours=2)
    timestamp2 = datetime.now() - timedelta(hours=1)
    sample_feature_view.push_features(
        "test_features",
        "user456",
        {"avg_transaction_value": 100.0, "transaction_count": 3},
        event_timestamp=timestamp1,
    )
    sample_feature_view.push_features(
        "test_features",
        "user456",
        {"avg_transaction_value": 200.0, "transaction_count": 7},
        event_timestamp=timestamp2,
    )
    retrieved_features = sample_feature_view.get_online_features(
        "test_features", "user456"
    )
    assert retrieved_features["avg_transaction_value"] == 200.0
    assert retrieved_features["transaction_count"] == 7


def test_get_historical_features(sample_feature_view: Any) -> Any:
    """Test retrieving historical features."""
    timestamp1 = datetime(2023, 1, 10, 10, 0, 0)
    timestamp2 = datetime(2023, 1, 10, 12, 0, 0)
    sample_feature_view.push_features(
        "test_features",
        "user789",
        {"avg_transaction_value": 50.0, "transaction_count": 1},
        event_timestamp=timestamp1,
    )
    sample_feature_view.push_features(
        "test_features",
        "user789",
        {"avg_transaction_value": 75.0, "transaction_count": 2},
        event_timestamp=timestamp2,
    )
    entity_data = pd.DataFrame(
        {
            "entity_id": ["user789", "user789"],
            "timestamp": [
                datetime(2023, 1, 10, 11, 0, 0),
                datetime(2023, 1, 10, 13, 0, 0),
            ],
        }
    )
    historical_data = sample_feature_view.get_historical_features(
        "test_features", entity_data
    )
    assert historical_data.iloc[0]["avg_transaction_value"] == 50.0
    assert historical_data.iloc[0]["transaction_count"] == 1
    assert historical_data.iloc[1]["avg_transaction_value"] == 75.0
    assert historical_data.iloc[1]["transaction_count"] == 2


def test_get_specific_features(sample_feature_view: Any, sample_features: Any) -> Any:
    """Test retrieving specific features."""
    sample_feature_view.push_features("test_features", "user123", sample_features)
    retrieved_features = sample_feature_view.get_online_features(
        "test_features", "user123", ["transaction_count"]
    )
    assert "transaction_count" in retrieved_features
    assert "avg_transaction_value" not in retrieved_features
    assert (
        retrieved_features["transaction_count"] == sample_features["transaction_count"]
    )


def test_entity_not_found(sample_feature_view: Any) -> Any:
    """Test behavior when entity is not found."""
    retrieved_features = sample_feature_view.get_online_features(
        "test_features", "nonexistent_user"
    )
    assert retrieved_features == {}


def test_feature_view_not_found(feature_store: Any) -> Any:
    """Test behavior when feature view is not found."""
    with pytest.raises(KeyError):
        feature_store.get_online_features("nonexistent_view", "user123")


def test_delete_feature_view(sample_feature_view: Any, sample_features: Any) -> Any:
    """Test deleting a feature view."""
    sample_feature_view.push_features("test_features", "user123", sample_features)
    result = sample_feature_view.delete_feature_view("test_features")
    assert result is True
    feature_views = sample_feature_view.list_feature_views()
    assert "test_features" not in feature_views
    result = sample_feature_view.delete_feature_view("test_features")
    assert result is False


def test_multiple_feature_views(feature_store: Any) -> Any:
    """Test managing multiple feature views."""
    feature_store.register_feature_view(
        feature_view_name="user_features",
        entity_keys=["user_id"],
        features=["login_count", "session_duration"],
    )
    feature_store.register_feature_view(
        feature_view_name="device_features",
        entity_keys=["device_id"],
        features=["battery_level", "signal_strength"],
    )
    feature_store.push_features(
        "user_features", "user123", {"login_count": 10, "session_duration": 3600}
    )
    feature_store.push_features(
        "device_features", "device456", {"battery_level": 0.75, "signal_strength": 0.85}
    )
    feature_views = feature_store.list_feature_views()
    assert "user_features" in feature_views
    assert "device_features" in feature_views
    user_features = feature_store.get_online_features("user_features", "user123")
    device_features = feature_store.get_online_features("device_features", "device456")
    assert user_features["login_count"] == 10
    assert device_features["battery_level"] == 0.75
