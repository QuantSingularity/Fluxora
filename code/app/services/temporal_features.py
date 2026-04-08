"""Temporal / cyclical feature creation using pandas."""

import numpy as np
import pandas as pd


def create_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds sine/cosine cyclical encodings for hour, day_of_week, and month.
    Expects columns 'hour', 'day_of_week', and 'month' to already exist.
    """
    df = df.copy()
    if "hour" in df.columns:
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    if "day_of_week" in df.columns:
        df["day_of_week_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["day_of_week_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

    if "month" in df.columns:
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    return df


def create_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds an 'is_holiday' flag based on US federal holidays and cyclical time features.
    Accepts either a DatetimeIndex or a 'timestamp' column.
    """
    df = df.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        if "timestamp" in df.columns:
            df = df.set_index(pd.to_datetime(df["timestamp"]))
        else:
            raise ValueError(
                "DataFrame must have a DatetimeIndex or a 'timestamp' column."
            )

    try:
        from pandas.tseries.holiday import USFederalHolidayCalendar

        cal = USFederalHolidayCalendar()
        holidays = cal.holidays(start=df.index.min(), end=df.index.max())
        df["is_holiday"] = df.index.normalize().isin(holidays).astype(int)
    except Exception:
        df["is_holiday"] = 0

    if "hour" not in df.columns:
        df["hour"] = df.index.hour
    if "day_of_week" not in df.columns:
        df["day_of_week"] = df.index.dayofweek
    if "month" not in df.columns:
        df["month"] = df.index.month

    df = create_cyclical_features(df)
    return df
