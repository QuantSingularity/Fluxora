import os
import sys
import unittest
from typing import Any
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import logging
from code.core.health_check import DependencyStatus, HealthCheck, HealthStatus
from code.core.metrics import MetricsCollector
from code.core.tracing import TracingManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TestMonitoringIntegration(unittest.TestCase):
    """
    Integration tests for monitoring and observability components working together
    """

    @patch("src.utils.metrics.start_http_server")
    @patch("src.utils.metrics.Counter")
    @patch("src.utils.metrics.Histogram")
    def test_metrics_with_logging(
        self, mock_histogram: Any, mock_counter: Any, mock_start_http_server: Any
    ) -> Any:
        """Test that metrics and logging work together"""
        mock_counter_instance = Mock()
        mock_counter.return_value = mock_counter_instance
        mock_counter_instance.labels.return_value = mock_counter_instance
        mock_histogram_instance = Mock()
        mock_histogram.return_value = mock_histogram_instance
        mock_histogram_instance.labels.return_value = mock_histogram_instance
        metrics = MetricsCollector(service_name="test_service")
        logger = setup_logging(service_name="test_service")
        set_request_context(request_id="req123", user_id="user456")

        @metrics.request_timer(method="GET", endpoint="/test")
        def test_function():
            logger.info("Processing request", extra={"endpoint": "/test"})
            return "success"

        result = test_function()
        self.assertEqual(result, "success")
        mock_counter_instance.labels.assert_called_with(
            method="GET", endpoint="/test", status=200
        )
        mock_counter_instance.inc.assert_called_once()
        mock_histogram_instance.labels.assert_called_with(
            method="GET", endpoint="/test"
        )
        mock_histogram_instance.observe.assert_called_once()
        clear_request_context()

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_with_metrics(
        self, mock_disk_usage: Any, mock_virtual_memory: Any, mock_cpu_percent: Any
    ) -> Any:
        """Test that health checks and metrics work together"""
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)
        health_check = HealthCheck(service_name="test_service")
        metrics = MetricsCollector(service_name="test_service")

        def check_database():
            metrics.set_resource_usage("database", "latency_ms", 15.0)
            return DependencyStatus(
                name="database",
                status=HealthStatus.HEALTHY,
                details={"latency_ms": 15.0},
            )

        health_check.add_dependency_check(check_database)
        health_status = health_check.check_health()
        self.assertEqual(health_status["status"], HealthStatus.HEALTHY)
        self.assertEqual(health_status["dependencies"]["items"][0]["name"], "database")
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.HEALTHY
        )

    @patch("src.utils.tracing.trace")
    def test_tracing_with_metrics_and_logging(self, mock_trace: Any) -> Any:
        """Test that tracing, metrics, and logging work together"""
        mock_tracer_provider = Mock()
        mock_trace.get_tracer_provider.return_value = mock_tracer_provider
        mock_tracer = Mock()
        mock_trace.get_tracer.return_value = mock_tracer
        mock_span = Mock()
        mock_tracer.start_as_current_span.return_value.__enter__.return_value = (
            mock_span
        )
        tracing = TracingManager(service_name="test_service")
        metrics = MetricsCollector(service_name="test_service")
        logger = setup_logging(service_name="test_service")
        set_request_context(request_id="req123", user_id="user456")

        @tracing.trace_function(name="test_operation")
        @metrics.request_timer(method="GET", endpoint="/test")
        def test_function(param1, param2="default"):
            logger.info(
                "Processing request",
                extra={"endpoint": "/test", "param1": param1, "param2": param2},
            )
            return f"{param1}-{param2}"

        result = test_function("value1", param2="value2")
        self.assertEqual(result, "value1-value2")
        mock_tracer.start_as_current_span.assert_called_with("test_operation")
        mock_span.set_attribute.assert_any_call("arg_0", "value1")
        mock_span.set_attribute.assert_any_call("kwarg_param2", "value2")
        clear_request_context()


if __name__ == "__main__":
    unittest.main()
