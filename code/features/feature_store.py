from typing import Any, Dict
import numpy as np
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class FeatureStore:
    """
    Simple feature store implementation to replace Feast dependency
    """

    def __init__(self, repo_path: Any = None) -> None:
        self.features: Dict[str, Any] = {}

    def get_online_features(self, entity_rows: Any, features: Any) -> Any:
        """
        Simulate getting online features
        """
        result = {}
        for feature in features:
            feature_name = feature.split(":")[-1]
            if "lag_24h" in feature_name:
                result[feature_name] = np.random.uniform(10, 50, size=len(entity_rows))
            elif "rolling_7d_mean" in feature_name:
                result[feature_name] = np.random.uniform(20, 40, size=len(entity_rows))
            elif "temperature" in feature_name:
                result[feature_name] = np.random.uniform(15, 30, size=len(entity_rows))
            elif "humidity" in feature_name:
                result[feature_name] = np.random.uniform(30, 80, size=len(entity_rows))
            else:
                result[feature_name] = np.random.uniform(0, 100, size=len(entity_rows))
        for i, entity_row in enumerate(entity_rows):
            for key, value in entity_row.items():
                if key not in result:
                    result[key] = [None] * len(entity_rows)  # type: ignore[assignment]
                result[key][i] = value
        return pd.DataFrame(result)

    def materialize(self, start_date: Any, end_date: Any) -> Any:
        """
        Mock implementation of materialize
        """
        logger.info(f"Materializing features from {start_date} to {end_date}")
        return True


def get_feature_store() -> Any:
    """
    Get the feature store instance

    Returns:
        FeatureStore: The feature store instance
    """
    return FeatureStore(repo_path="./config/feature_store")


def get_online_features(entity_rows: Any, feature_refs: Any) -> Any:
    """
    Get online features from the feature store

    Args:
        entity_rows: List of entity dictionaries
        feature_refs: List of feature references

    Returns:
        DataFrame: Features for the provided entities
    """
    store = get_feature_store()
    return store.get_online_features(entity_rows=entity_rows, features=feature_refs)


def materialize_features(start_date: Any, end_date: Any) -> Any:
    """
    Materialize features for a date range

    Args:
        start_date: Start date for materialization
        end_date: End date for materialization
    """
    store = get_feature_store()
    store.materialize(start_date=start_date, end_date=end_date)
