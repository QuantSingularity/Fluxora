import os
import sys
import unittest
from typing import Any
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from code.core.metrics import MetricsCollector


class TestMetrics(unittest.TestCase):

    def setUp(self) -> Any:
        from prometheus_client import REGISTRY

        collectors = list(REGISTRY._collector_to_names.keys())
        for collector in collectors:
            REGISTRY.unregister(collector)

    @patch("src.utils.metrics.start_http_server")
    def test_start_metrics_server(self, mock_start_http_server: Any) -> Any:
        """Test that start_metrics_server calls the Prometheus server start function"""
        collector = MetricsCollector(service_name="test_service", port=8000)
        collector.start_metrics_server()
        mock_start_http_server.assert_called_once_with(8000)

    @patch("src.utils.metrics.Counter")
    @patch("src.utils.metrics.Histogram")
    def test_track_request(self, mock_histogram: Any, mock_counter: Any) -> Any:
        """Test that track_request increments the counter and observes the histogram"""
        mock_counter_instance = Mock()
        mock_counter.return_value = mock_counter_instance
        mock_counter_instance.labels.return_value = mock_counter_instance
        mock_histogram_instance = Mock()
        mock_histogram.return_value = mock_histogram_instance
        mock_histogram_instance.labels.return_value = mock_histogram_instance
        collector = MetricsCollector(service_name="test_service")
        collector.track_request(method="GET", endpoint="/test", status=200, latency=0.1)
        mock_counter_instance.labels.assert_called_with(
            method="GET", endpoint="/test", status=200
        )
        mock_counter_instance.inc.assert_called_once()
        mock_histogram_instance.labels.assert_called_with(
            method="GET", endpoint="/test"
        )
        mock_histogram_instance.observe.assert_called_with(0.1)

    @patch("src.utils.metrics.Counter")
    def test_track_error(self, mock_counter: Any) -> Any:
        """Test that track_error increments the error counter"""
        mock_counter_instance = Mock()
        mock_counter.return_value = mock_counter_instance
        mock_counter_instance.labels.return_value = mock_counter_instance
        collector = MetricsCollector(service_name="test_service")
        collector.track_error(error_type="validation", error_code="invalid_input")
        mock_counter_instance.labels.assert_called_with(
            type="validation", code="invalid_input"
        )
        mock_counter_instance.inc.assert_called_once()

    @patch("src.utils.metrics.Gauge")
    def test_set_circuit_breaker_state(self, mock_gauge: Any) -> Any:
        """Test that set_circuit_breaker_state sets the gauge value"""
        mock_gauge_instance = Mock()
        mock_gauge.return_value = mock_gauge_instance
        mock_gauge_instance.labels.return_value = mock_gauge_instance
        collector = MetricsCollector(service_name="test_service")
        collector.set_circuit_breaker_state(name="user_service", state=1)
        mock_gauge_instance.labels.assert_called_with(name="user_service")
        mock_gauge_instance.set.assert_called_with(1)

    @patch("src.utils.metrics.Gauge")
    def test_set_resource_usage(self, mock_gauge: Any) -> Any:
        """Test that set_resource_usage sets the gauge value"""
        mock_gauge_instance = Mock()
        mock_gauge.return_value = mock_gauge_instance
        mock_gauge_instance.labels.return_value = mock_gauge_instance
        collector = MetricsCollector(service_name="test_service")
        collector.set_resource_usage(resource="cpu", unit="percent", value=75.5)
        mock_gauge_instance.labels.assert_called_with(resource="cpu", unit="percent")
        mock_gauge_instance.set.assert_called_with(75.5)

    @patch("src.utils.metrics.Gauge")
    def test_set_prediction_accuracy(self, mock_gauge: Any) -> Any:
        """Test that set_prediction_accuracy sets the gauge value"""
        mock_gauge_instance = Mock()
        mock_gauge.return_value = mock_gauge_instance
        mock_gauge_instance.labels.return_value = mock_gauge_instance
        collector = MetricsCollector(service_name="test_service")
        collector.set_prediction_accuracy(
            model="energy_forecast", metric="rmse", value=0.85
        )
        mock_gauge_instance.labels.assert_called_with(
            model="energy_forecast", metric="rmse"
        )
        mock_gauge_instance.set.assert_called_with(0.85)

    @patch("src.utils.metrics.MetricsCollector.track_request")
    @patch("src.utils.metrics.MetricsCollector.track_error")
    def test_request_timer_success(
        self, mock_track_error: Any, mock_track_request: Any
    ) -> Any:
        """Test that request_timer decorator tracks successful requests"""
        collector = MetricsCollector(service_name="test_service")

        @collector.request_timer(method="GET", endpoint="/test")
        def success_func():
            return "success"

        result = success_func()
        self.assertEqual(result, "success")
        mock_track_request.assert_called_once()
        self.assertEqual(mock_track_request.call_args[0][0], "GET")
        self.assertEqual(mock_track_request.call_args[0][1], "/test")
        self.assertEqual(mock_track_request.call_args[0][2], 200)
        self.assertIsInstance(mock_track_request.call_args[0][3], float)
        mock_track_error.assert_not_called()

    @patch("src.utils.metrics.MetricsCollector.track_request")
    @patch("src.utils.metrics.MetricsCollector.track_error")
    def test_request_timer_failure(
        self, mock_track_error: Any, mock_track_request: Any
    ) -> Any:
        """Test that request_timer decorator tracks failed requests"""
        collector = MetricsCollector(service_name="test_service")

        @collector.request_timer(method="GET", endpoint="/test")
        def failure_func():
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            failure_func()
        mock_track_request.assert_called_once()
        self.assertEqual(mock_track_request.call_args[0][0], "GET")
        self.assertEqual(mock_track_request.call_args[0][1], "/test")
        self.assertEqual(mock_track_request.call_args[0][2], 500)
        self.assertIsInstance(mock_track_request.call_args[0][3], float)
        mock_track_error.assert_called_once_with("exception", "ValueError")


if __name__ == "__main__":
    unittest.main()
