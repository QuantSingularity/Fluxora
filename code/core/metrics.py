import time
from typing import Any, Callable

from prometheus_client import Counter, Gauge, Histogram, start_http_server

_metrics_server_started = False


class MetricsCollector:
    """
    Metrics collector for Prometheus. Uses a unique registry per service_name
    to avoid duplicate-metric errors in multi-instance environments.
    """

    def __init__(self, service_name: str, port: int = 9090) -> None:
        self.service_name = service_name
        self.port = port

        safe_name = service_name.replace("-", "_").replace(".", "_")

        self.request_counter = Counter(
            f"{safe_name}_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
        )
        self.request_latency = Histogram(
            f"{safe_name}_request_latency_seconds",
            "Request latency in seconds",
            ["method", "endpoint"],
            buckets=(
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
                float("inf"),
            ),
        )
        self.error_counter = Counter(
            f"{safe_name}_errors_total",
            "Total number of errors",
            ["type", "code"],
        )
        self.circuit_breaker_state = Gauge(
            f"{safe_name}_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 2=half-open)",
            ["name"],
        )
        self.resource_usage = Gauge(
            f"{safe_name}_resource_usage",
            "Resource usage",
            ["resource", "unit"],
        )
        self.prediction_accuracy = Gauge(
            f"{safe_name}_prediction_accuracy",
            "Prediction accuracy",
            ["model", "metric"],
        )

    def start_metrics_server(self) -> None:
        """Start the Prometheus metrics HTTP server (idempotent)."""
        global _metrics_server_started
        if not _metrics_server_started:
            start_http_server(self.port)
            _metrics_server_started = True

    def track_request(
        self, method: str, endpoint: str, status: int, latency: float
    ) -> None:
        self.request_counter.labels(
            method=method, endpoint=endpoint, status=str(status)
        ).inc()
        self.request_latency.labels(method=method, endpoint=endpoint).observe(latency)

    def track_error(self, error_type: str, error_code: str) -> None:
        self.error_counter.labels(type=error_type, code=error_code).inc()

    def set_circuit_breaker_state(self, name: str, state: int) -> None:
        self.circuit_breaker_state.labels(name=name).set(state)

    def set_resource_usage(self, resource: str, unit: str, value: float) -> None:
        self.resource_usage.labels(resource=resource, unit=unit).set(value)

    def set_prediction_accuracy(self, model: str, metric: str, value: float) -> None:
        self.prediction_accuracy.labels(model=model, metric=metric).set(value)

    def request_timer(self, method: str, endpoint: str) -> Any:
        """Decorator for tracking request latency and status."""

        def decorator(func: Callable) -> Callable:
            import functools

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                http_status = 200
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    http_status = 500
                    self.track_error("exception", type(e).__name__)
                    raise
                finally:
                    latency = time.time() - start_time
                    self.track_request(method, endpoint, http_status, latency)

            return wrapper

        return decorator
