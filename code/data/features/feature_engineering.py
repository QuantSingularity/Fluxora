from typing import List

import pandas as pd


def create_time_series_features(
    df: pd.DataFrame, time_col: str = "timestamp"
) -> pd.DataFrame:
    """
    Creates time-series features from a timestamp column.

    Args:
        df: DataFrame containing the time-series data.
        time_col: Name of the timestamp column.

    Returns:
        DataFrame with new time-series features.
    """
    df[time_col] = pd.to_datetime(df[time_col])
    df["hour"] = df[time_col].dt.hour
    df["day_of_week"] = df[time_col].dt.dayofweek  # Monday=0, Sunday=6
    df["day_of_year"] = df[time_col].dt.dayofyear
    df["month"] = df[time_col].dt.month
    df["year"] = df[time_col].dt.year
    df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
    df["quarter"] = df[time_col].dt.quarter

    return df


def create_lag_features(
    df: pd.DataFrame, target_col: str, lags: List[int]
) -> pd.DataFrame:
    """
    Creates lag features for a given target column.

    Args:
        df: DataFrame containing the time-series data.
        target_col: Name of the column to create lags for (e.g., 'consumption_kwh').
        lags: List of lag periods (e.g., [1, 2, 24] for 1, 2, and 24 periods ago).

    Returns:
        DataFrame with new lag features.
    """
    for lag in lags:
        df[f"{target_col}_lag_{lag}"] = df[target_col].shift(lag)

    return df


def create_rolling_features(
    df: pd.DataFrame, target_col: str, windows: List[int]
) -> pd.DataFrame:
    """
    Creates rolling window features (mean, std) for a given target column.

    Args:
        df: DataFrame containing the time-series data.
        target_col: Name of the column to create rolling features for.
        windows: List of window sizes (e.g., [3, 7, 30]).

    Returns:
        DataFrame with new rolling features.
    """
    for window in windows:
        df[f"{target_col}_rolling_mean_{window}"] = (
            df[target_col].rolling(window=window).mean()
        )
        df[f"{target_col}_rolling_std_{window}"] = (
            df[target_col].rolling(window=window).std()
        )

    return df


def preprocess_data_for_model(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies a full feature engineering pipeline to the raw data.

    Args:
        df: Raw DataFrame with 'timestamp' and 'consumption_kwh'.

    Returns:
        Processed DataFrame ready for model training/prediction.
    """
    # 1. Create time-series features
    df = create_time_series_features(df, time_col="timestamp")

    # 2. Create lag features (e.g., last 1, 2, and 24 hours)
    df = create_lag_features(df, "consumption_kwh", [1, 2, 24])

    # 3. Create rolling features (e.g., 3-hour and 7-day rolling mean)
    df = create_rolling_features(df, "consumption_kwh", [3, 24 * 7])

    # 4. Handle NaNs created by lag/rolling features (e.g., fill with 0 or drop)
    # For simplicity, we'll drop the first rows with NaNs
    df = df.dropna()

    return df
