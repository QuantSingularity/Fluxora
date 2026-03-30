from typing import Any

"""
Tests for visualization components.
"""

import numpy as np
import pandas as pd
import pytest
from code.visualization.charts import (
    create_bar_chart,
    create_heatmap,
    create_line_chart,
    create_scatter_plot,
)


@pytest.fixture
def time_series_data() -> Any:
    """Create sample time series data."""
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2024-01-01", periods=10, freq="H"),
            "value": np.random.normal(100, 10, 10),
            "category": ["A", "B"] * 5,
        }
    )


@pytest.fixture
def categorical_data() -> Any:
    """Create sample categorical data."""
    return pd.DataFrame(
        {
            "category": ["A", "B", "C", "D"],
            "value": [10, 20, 15, 25],
            "group": ["X", "X", "Y", "Y"],
        }
    )


@pytest.fixture
def correlation_data() -> Any:
    """Create sample correlation data."""
    return pd.DataFrame(
        {
            "var1": np.random.normal(0, 1, 100),
            "var2": np.random.normal(0, 1, 100),
            "var3": np.random.normal(0, 1, 100),
        }
    )


def test_create_line_chart(time_series_data: Any) -> Any:
    """Test line chart creation."""
    chart = create_line_chart(
        data=time_series_data, x="timestamp", y="value", title="Test Line Chart"
    )
    assert chart is not None
    assert chart.title == "Test Line Chart"
    assert len(chart.data) > 0


def test_create_line_chart_with_missing_data() -> Any:
    """Test line chart creation with missing data."""
    data = pd.DataFrame(
        {
            "timestamp": pd.date_range(start="2024-01-01", periods=5, freq="H"),
            "value": [1, np.nan, 3, np.nan, 5],
        }
    )
    chart = create_line_chart(
        data=data, x="timestamp", y="value", title="Line Chart with Missing Data"
    )
    assert chart is not None
    assert len(chart.data) > 0


def test_create_bar_chart(categorical_data: Any) -> Any:
    """Test bar chart creation."""
    chart = create_bar_chart(
        data=categorical_data, x="category", y="value", title="Test Bar Chart"
    )
    assert chart is not None
    assert chart.title == "Test Bar Chart"
    assert len(chart.data) > 0


def test_create_bar_chart_with_grouping(categorical_data: Any) -> Any:
    """Test grouped bar chart creation."""
    chart = create_bar_chart(
        data=categorical_data,
        x="category",
        y="value",
        color="group",
        title="Grouped Bar Chart",
    )
    assert chart is not None
    assert len(chart.data) > 1


def test_create_heatmap(correlation_data: Any) -> Any:
    """Test heatmap creation."""
    chart = create_heatmap(data=correlation_data, title="Correlation Heatmap")
    assert chart is not None
    assert chart.title == "Correlation Heatmap"
    assert len(chart.data) > 0


def test_create_heatmap_with_custom_colors(correlation_data: Any) -> Any:
    """Test heatmap creation with custom colors."""
    chart = create_heatmap(
        data=correlation_data, title="Custom Heatmap", colorscale="Viridis"
    )
    assert chart is not None
    assert chart.colorscale == "Viridis"


def test_create_scatter_plot(correlation_data: Any) -> Any:
    """Test scatter plot creation."""
    chart = create_scatter_plot(
        data=correlation_data, x="var1", y="var2", title="Scatter Plot"
    )
    assert chart is not None
    assert chart.title == "Scatter Plot"
    assert len(chart.data) > 0


def test_create_scatter_plot_with_color(correlation_data: Any) -> Any:
    """Test scatter plot with color encoding."""
    chart = create_scatter_plot(
        data=correlation_data,
        x="var1",
        y="var2",
        color="var3",
        title="Colored Scatter Plot",
    )
    assert chart is not None
    assert len(chart.data) > 0


@pytest.mark.integration
def test_chart_export(time_series_data: Any) -> Any:
    """Test chart export functionality."""
    chart = create_line_chart(
        data=time_series_data, x="timestamp", y="value", title="Export Test"
    )
    png_data = chart.to_image(format="png")
    assert png_data is not None
    assert len(png_data) > 0
    html_data = chart.to_html()
    assert html_data is not None
    assert "plotly" in html_data


def test_chart_customization(time_series_data: Any) -> Any:
    """Test chart customization options."""
    chart = create_line_chart(
        data=time_series_data,
        x="timestamp",
        y="value",
        title="Customized Chart",
        xlabel="Time",
        ylabel="Value",
        theme="dark",
    )
    assert chart is not None
    assert chart.layout.xaxis.title.text == "Time"
    assert chart.layout.yaxis.title.text == "Value"
    assert chart.layout.template == "plotly_dark"


def test_chart_error_handling() -> Any:
    """Test chart error handling."""
    with pytest.raises(ValueError):
        create_line_chart(data=pd.DataFrame(), x="timestamp", y="value")
    with pytest.raises(KeyError):
        create_line_chart(data=time_series_data, x="nonexistent", y="value")
    with pytest.raises(TypeError):
        create_line_chart(data=time_series_data, x="timestamp", y="category")
