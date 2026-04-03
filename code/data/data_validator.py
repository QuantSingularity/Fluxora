"""
Data validation utilities for Fluxora.
Uses pandas-based validation to avoid the great_expectations dependency.
"""

from typing import Any, Dict, List, Optional

import pandas as pd


class DataValidationError(Exception):
    """Exception raised when data validation fails."""


class ValidationResult:
    def __init__(self, success: bool, errors: Optional[List[str]] = None) -> None:
        self.success = success
        self.errors = errors or []

    def __repr__(self) -> str:
        return f"ValidationResult(success={self.success}, errors={self.errors})"


def validate_raw_data(df: Any) -> ValidationResult:
    """
    Validates a raw energy DataFrame for required columns and value ranges.

    Args:
        df: A pandas DataFrame containing the raw data.

    Returns:
        ValidationResult with success flag and list of error messages.

    Raises:
        DataValidationError: if validation fails.
    """
    errors: List[str] = []

    required_columns = ["timestamp", "consumption_kwh"]
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")

    if errors:
        raise DataValidationError(f"Data validation failed: {errors}")

    if df["consumption_kwh"].isnull().any():
        errors.append("Column 'consumption_kwh' contains null values.")

    if (df["consumption_kwh"].dropna() < 0).any():
        errors.append("Column 'consumption_kwh' contains negative values.")

    if "cost_usd" in df.columns:
        if df["cost_usd"].dropna().lt(0).any():
            errors.append("Column 'cost_usd' contains negative values.")

    if "temperature_c" in df.columns:
        temp_valid = df["temperature_c"].dropna()
        if (temp_valid < -100).any() or (temp_valid > 100).any():
            errors.append(
                "Column 'temperature_c' has values outside plausible range [-100, 100]."
            )

    if "humidity_percent" in df.columns:
        hum_valid = df["humidity_percent"].dropna()
        if (hum_valid < 0).any() or (hum_valid > 100).any():
            errors.append(
                "Column 'humidity_percent' has values outside range [0, 100]."
            )

    if errors:
        raise DataValidationError(f"Data validation failed: {errors}")

    return ValidationResult(success=True)


def validate_energy_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive validation with a summary report instead of raising.

    Returns:
        dict with 'valid', 'row_count', 'null_counts', and 'warnings' keys.
    """
    warnings: List[str] = []

    if df.empty:
        return {
            "valid": False,
            "row_count": 0,
            "null_counts": {},
            "warnings": ["DataFrame is empty."],
        }

    null_counts = df.isnull().sum().to_dict()

    if "consumption_kwh" in df.columns and df["consumption_kwh"].isnull().any():
        warnings.append(
            f"consumption_kwh has {null_counts.get('consumption_kwh', 0)} null values."
        )

    if "timestamp" in df.columns:
        try:
            pd.to_datetime(df["timestamp"])
        except Exception:
            warnings.append("Some 'timestamp' values could not be parsed as datetime.")

    return {
        "valid": len(warnings) == 0,
        "row_count": len(df),
        "null_counts": null_counts,
        "warnings": warnings,
    }
