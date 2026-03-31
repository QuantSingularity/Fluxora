import functools
from typing import Any, Callable, Dict, Optional

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class TracingManager:
    """
    Manager for distributed tracing
    """

    def __init__(
        self, service_name: str, jaeger_host: str = "jaeger", jaeger_port: int = 6831
    ) -> None:
        self.service_name = service_name
        resource = Resource(attributes={SERVICE_NAME: service_name})
        trace.set_tracer_provider(TracerProvider(resource=resource))
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host, agent_port=jaeger_port
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        self.tracer = trace.get_tracer(service_name)
        self.propagator = TraceContextTextMapPropagator()

    def trace_function(self, name: Optional[str] = None) -> Any:
        """
        Decorator for tracing a function
        """

        def decorator(func: Callable) -> Callable:

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                span_name = name or func.__name__
                with self.tracer.start_as_current_span(span_name) as span:
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
                        span.record_exception(e)
                        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                        raise

            return wrapper

        return decorator

    def extract_context_from_headers(
        self, headers: Dict[str, str]
    ) -> trace.SpanContext:
        """
        Extract trace context from HTTP headers
        """
        return self.propagator.extract(headers)

    def inject_context_into_headers(self, headers: Dict[str, str]) -> Any:
        """
        Inject current trace context into HTTP headers
        """
        self.propagator.inject(headers)
