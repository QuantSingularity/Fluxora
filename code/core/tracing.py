import functools
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    _OPENTELEMETRY_AVAILABLE = True
except ImportError:
    _OPENTELEMETRY_AVAILABLE = False
    logger.info(
        "opentelemetry packages not installed. Tracing will be disabled. "
        "Install with: pip install opentelemetry-api opentelemetry-sdk "
        "opentelemetry-exporter-jaeger"
    )


class NoOpTracer:
    """No-op tracer used when opentelemetry is not available."""

    def start_as_current_span(self, name: str):
        from contextlib import contextmanager

        @contextmanager
        def _noop():
            yield None

        return _noop()

    def set_attribute(self, key: str, value: Any) -> None:
        pass


class TracingManager:
    """
    Manager for distributed tracing. Falls back to no-op if opentelemetry
    is not installed.
    """

    def __init__(
        self, service_name: str, jaeger_host: str = "jaeger", jaeger_port: int = 6831
    ) -> None:
        self.service_name = service_name
        self._enabled = _OPENTELEMETRY_AVAILABLE

        if self._enabled:
            resource = Resource(attributes={SERVICE_NAME: service_name})
            trace.set_tracer_provider(TracerProvider(resource=resource))
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_host, agent_port=jaeger_port
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            self.tracer = trace.get_tracer(service_name)
            self.propagator = TraceContextTextMapPropagator()
        else:
            self.tracer = NoOpTracer()
            self.propagator = None

    def trace_function(self, name: Optional[str] = None) -> Any:
        """
        Decorator for tracing a function
        """

        def decorator(func: Callable) -> Callable:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                span_name = name or func.__name__
                with self.tracer.start_as_current_span(span_name) as span:
                    if span is not None and self._enabled:
                        for i, arg in enumerate(args):
                            if isinstance(arg, (str, int, float, bool)):
                                span.set_attribute(f"arg_{i}", str(arg))
                        for key, value in kwargs.items():
                            if isinstance(value, (str, int, float, bool)):
                                span.set_attribute(f"kwarg_{key}", str(value))
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        if span is not None and self._enabled:
                            span.record_exception(e)
                            span.set_status(
                                trace.Status(trace.StatusCode.ERROR, str(e))
                            )
                        raise

            return wrapper

        return decorator

    def extract_context_from_headers(self, headers: Dict[str, str]) -> Any:
        """
        Extract trace context from HTTP headers
        """
        if not self._enabled or self.propagator is None:
            return None
        return self.propagator.extract(headers)

    def inject_context_into_headers(self, headers: Dict[str, str]) -> None:
        """
        Inject current trace context into HTTP headers
        """
        if not self._enabled or self.propagator is None:
            return
        self.propagator.inject(headers)
