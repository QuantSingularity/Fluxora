from typing import Any

import numpy as np
import pandas as pd
from core.config import get_config


class FeaturePipeline:
    """
    Pipeline for transforming raw data into features for model prediction
    """

    def __init__(self) -> None:
        self.config = get_config()
        self.preprocessing_config = self.config.get("preprocessing", {})

    def transform(self, data: Any) -> Any:
        """
        Transform raw data into features for model prediction.

        Args:
            data: PredictionRequest object containing timestamps, meter_ids,
                  and context_features.

        Returns:
            Processed features (numpy array) ready for model prediction.
        """
        df = pd.DataFrame({"timestamp": data.timestamps, "meter_id": data.meter_ids})

        for feature_name, values in data.context_features.items():
            if isinstance(values, list):
                if len(values) == len(df):
                    df[feature_name] = values
                else:
                    # Broadcast scalar or warn about length mismatch
                    if len(values) == 1:
                        df[feature_name] = values[0]
                    else:
                        raise ValueError(
                            f"Context feature '{feature_name}' has length "
                            f"{len(values)} but expected {len(df)}."
                        )
            else:
                df[feature_name] = values

        df = self._extract_temporal_features(df)

        if self.preprocessing_config.get("normalize", True):
            df = self._normalize_features(df)

        feature_cols = self._get_feature_columns()
        # Only keep columns that exist in the dataframe
        available = [c for c in feature_cols if c in df.columns]
        features = df[available].values
        return features

    def _extract_temporal_features(self, df: Any) -> Any:
        """Extract temporal features from timestamp"""
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["month"] = df["timestamp"].dt.month
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
        df["day_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
        return df

    def _normalize_features(self, df: Any) -> Any:
        """Normalize numerical features using z-score standardisation."""
        num_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        skip = {"meter_id"}
        for col in num_cols:
            if col in skip:
                continue
            mean = self.preprocessing_config.get(f"mean_{col}", df[col].mean())
            std = self.preprocessing_config.get(f"std_{col}", df[col].std())
            if std is not None and std > 0:
                df[col] = (df[col] - mean) / std
            # If std == 0 (constant column) we leave it as-is rather than
            # silently zeroing it out, which would lose the constant signal.
        return df

    def _get_feature_columns(self) -> Any:
        """Get the list of feature columns to use for the model"""
        default_features = [
            "hour_sin",
            "hour_cos",
            "day_sin",
            "day_cos",
            "month_sin",
            "month_cos",
            "is_weekend",
        ]
        context_features = self.preprocessing_config.get("context_features", [])
        return default_features + context_features
