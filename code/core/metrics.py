import time
from typing import Any, Callable

from prometheus_client import Counter, Gauge, Histogram, start_http_server


class MetricsCollector:
    """
    Metrics collector for Prometheus
    """

    def __init__(self, service_name: str, port: int = 8000) -> None:
        self.service_name = service_name
        self.port = port
        self.request_counter = Counter(
            f"{service_name}_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
        )
        self.request_latency = Histogram(
            f"{service_name}_request_latency_seconds",
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
            f"{service_name}_errors_total", "Total number of errors", ["type", "code"]
        )
        self.circuit_breaker_state = Gauge(
            f"{service_name}_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 2=half-open)",
            ["name"],
        )
        self.resource_usage = Gauge(
            f"{service_name}_resource_usage", "Resource usage", ["resource", "unit"]
        )
        self.prediction_accuracy = Gauge(
            f"{service_name}_prediction_accuracy",
            "Prediction accuracy",
            ["model", "metric"],
        )

    def start_metrics_server(self) -> Any:
        """
        Start the metrics server
        """
        start_http_server(self.port)

    def track_request(
        self, method: str, endpoint: str, status: int, latency: float
    ) -> Any:
        """
        Track a request
        """
        self.request_counter.labels(
            method=method, endpoint=endpoint, status=status
        ).inc()
        self.request_latency.labels(method=method, endpoint=endpoint).observe(latency)

    def track_error(self, error_type: str, error_code: str) -> Any:
        """
        Track an error
        """
        self.error_counter.labels(type=error_type, code=error_code).inc()

    def set_circuit_breaker_state(self, name: str, state: int) -> None:
        """
        Set circuit breaker state
        """
        self.circuit_breaker_state.labels(name=name).set(state)

    def set_resource_usage(self, resource: str, unit: str, value: float) -> None:
        """
        Set resource usage
        """
        self.resource_usage.labels(resource=resource, unit=unit).set(value)

    def set_prediction_accuracy(self, model: str, metric: str, value: float) -> None:
        """
        Set prediction accuracy
        """
        self.prediction_accuracy.labels(model=model, metric=metric).set(value)

    def request_timer(self, method: str, endpoint: str) -> Any:
        """
        Timer decorator for tracking request latency
        """

        def decorator(func: Callable) -> Callable:

            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    status = 200
                    return result
                except Exception as e:
                    status = 500
                    self.track_error("exception", type(e).__name__)
                    raise
                finally:
                    latency = time.time() - start_time
                    self.track_request(method, endpoint, status, latency)

            return wrapper

        return decorator
