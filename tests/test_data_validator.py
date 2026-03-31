"""
Unit tests for the data validation logic using Great Expectations.
"""

from code.data.data_validator import validate_raw_data
from typing import Any

import pandas as pd
import pytest


@pytest.fixture
def valid_data() -> Any:
    """Create valid test data."""
    return pd.DataFrame(
        {
            "Global_active_power": [1.5, 2.3, 3.1, 0.8, 1.2],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 5.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )


@pytest.fixture
def invalid_data_null() -> Any:
    """Create test data with null values."""
    return pd.DataFrame(
        {
            "Global_active_power": [1.5, None, 3.1, 0.8, 1.2],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 5.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )


@pytest.fixture
def invalid_data_range() -> Any:
    """Create test data with values outside valid range."""
    return pd.DataFrame(
        {
            "Global_active_power": [1.5, 25.3, 3.1, 0.8, 1.2],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 5.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )


@pytest.fixture
def invalid_data_relationship() -> Any:
    """Create test data with invalid relationship between columns."""
    return pd.DataFrame(
        {
            "Global_active_power": [1.5, 2.3, 3.1, 0.8, 1.2],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [260.2, 9.8, 13.2, 3.4, 5.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )


def test_validate_raw_data_valid(valid_data: Any) -> Any:
    """Test validation with valid data."""
    validate_raw_data(valid_data)


def test_validate_raw_data_null_values(invalid_data_null: Any) -> Any:
    """Test validation with null values."""
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(invalid_data_null)
    assert "Data validation failed" in str(excinfo.value)


def test_validate_raw_data_out_of_range(invalid_data_range: Any) -> Any:
    """Test validation with values outside valid range."""
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(invalid_data_range)
    assert "Data validation failed" in str(excinfo.value)


def test_validate_raw_data_invalid_relationship(invalid_data_relationship: Any) -> Any:
    """Test validation with invalid relationship between columns."""
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(invalid_data_relationship)
    assert "Data validation failed" in str(excinfo.value)


def test_validate_raw_data_empty() -> Any:
    """Test validation with empty DataFrame."""
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(pd.DataFrame())
    assert "Data validation failed" in str(excinfo.value)


def test_validate_raw_data_missing_columns() -> Any:
    """Test validation with missing required columns."""
    missing_columns_data = pd.DataFrame(
        {
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 239.8],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 5.0],
        }
    )
    with pytest.raises(Exception):
        validate_raw_data(missing_columns_data)


def test_validate_raw_data_edge_cases() -> Any:
    """Test validation with edge case values."""
    edge_case_data = pd.DataFrame(
        {
            "Global_active_power": [0.0, 20.0, 10.0, 5.0, 15.0],
            "Global_reactive_power": [0.2, 0.3, 0.1, 0.4, 0.2],
            "Voltage": [240.1, 238.5, 235.2, 241.3, 100.0],
            "Global_intensity": [6.2, 9.8, 13.2, 3.4, 100.0],
            "Sub_metering_1": [0, 1, 2, 0, 1],
            "Sub_metering_2": [1, 2, 3, 0, 2],
            "Sub_metering_3": [17, 18, 19, 16, 17],
        }
    )
    with pytest.raises(Exception) as excinfo:
        validate_raw_data(edge_case_data)
    assert "Data validation failed" in str(excinfo.value)
