"""Feature engineering utilities for Fluxora ML pipeline."""

from typing import List

import pandas as pd


def create_time_series_features(
    df: pd.DataFrame, time_col: str = "timestamp"
) -> pd.DataFrame:
    """Creates time-series features from a timestamp column."""
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])
    df["hour"] = df[time_col].dt.hour
    df["day_of_week"] = df[time_col].dt.dayofweek
    df["day_of_year"] = df[time_col].dt.dayofyear
    df["month"] = df[time_col].dt.month
    df["year"] = df[time_col].dt.year
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["quarter"] = df[time_col].dt.quarter
    return df


def create_lag_features(
    df: pd.DataFrame, target_col: str, lags: List[int]
) -> pd.DataFrame:
    """Creates lag features for a given target column."""
    df = df.copy()
    for lag in lags:
        df[f"{target_col}_lag_{lag}"] = df[target_col].shift(lag)
    return df


def create_rolling_features(
    df: pd.DataFrame, target_col: str, windows: List[int]
) -> pd.DataFrame:
    """Creates rolling window features (mean, std) for a given target column."""
    df = df.copy()
    for window in windows:
        df[f"{target_col}_rolling_mean_{window}"] = (
            df[target_col].rolling(window=window).mean()
        )
        df[f"{target_col}_rolling_std_{window}"] = (
            df[target_col].rolling(window=window).std()
        )
    return df


def preprocess_data_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """Applies a full feature engineering pipeline to the raw data.

    Drops rows where *any* engineered feature is NaN (typically the first
    ``max(lags + windows)`` rows that lack enough history).
    """
    df = create_time_series_features(df, time_col="timestamp")
    df = create_lag_features(df, "consumption_kwh", [1, 2, 24])
    df = create_rolling_features(df, "consumption_kwh", [3, 24 * 7])
    df = df.dropna()
    return df
