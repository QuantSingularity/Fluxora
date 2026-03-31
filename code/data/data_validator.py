from typing import Any

import great_expectations as ge


class DataValidationError(Exception):
    """Exception raised when data validation fails"""


def validate_raw_data(df: Any) -> Any:
    suite = ge.dataset.PandasDataset(df)
    suite.expect_column_values_to_not_be_null("Global_active_power")
    suite.expect_column_values_to_be_between(
        "Global_active_power", min_value=0, max_value=20
    )
    suite.expect_column_pair_values_A_to_be_greater_than_B(
        "Voltage", "Global_intensity"
    )
    validation_result = suite.validate()
    if not validation_result["success"]:
        raise DataValidationError(f"Data validation failed: {validation_result}")
