import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_forecast_vs_actual(forecast_df: Any) -> Any:
    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(
        go.Scatter(x=forecast_df["timestamp"], y=forecast_df["actual"], name="Actual"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_df["timestamp"], y=forecast_df["predicted"], name="Predicted"
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_df["timestamp"], y=forecast_df["residuals"], name="Residuals"
        ),
        row=2,
        col=1,
    )
    fig.update_layout(height=800, title="Forecast Analysis")
    return fig
