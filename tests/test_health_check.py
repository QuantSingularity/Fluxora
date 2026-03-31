import os
import sys
import unittest
from typing import Any
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from code.core.health_check import (
    DependencyStatus,
    HealthCheck,
    HealthStatus,
    add_health_check_endpoints,
)

from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestHealthCheck(unittest.TestCase):

    def test_dependency_status(self) -> Any:
        """Test that DependencyStatus correctly represents dependency status"""
        healthy_status = DependencyStatus(
            name="database", status=HealthStatus.HEALTHY, details={"latency_ms": 10}
        )
        self.assertEqual(healthy_status.name, "database")
        self.assertEqual(healthy_status.status, HealthStatus.HEALTHY)
        self.assertEqual(healthy_status.details, {"latency_ms": 10})
        status_dict = healthy_status.to_dict()
        self.assertEqual(status_dict["name"], "database")
        self.assertEqual(status_dict["status"], HealthStatus.HEALTHY)
        self.assertEqual(status_dict["details"], {"latency_ms": 10})
        unhealthy_status = DependencyStatus(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            details={"error": "Connection refused"},
        )
        self.assertEqual(unhealthy_status.name, "redis")
        self.assertEqual(unhealthy_status.status, HealthStatus.UNHEALTHY)
        self.assertEqual(unhealthy_status.details, {"error": "Connection refused"})

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_healthy(
        self, mock_disk_usage: Any, mock_virtual_memory: Any, mock_cpu_percent: Any
    ) -> Any:
        """Test that HealthCheck returns healthy status when all checks pass"""
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)
        health_check = HealthCheck(service_name="test_service")

        def check_database():
            return DependencyStatus(
                name="database", status=HealthStatus.HEALTHY, details={"latency_ms": 10}
            )

        health_check.add_dependency_check(check_database)
        health_status = health_check.check_health()
        self.assertEqual(health_status["status"], HealthStatus.HEALTHY)
        self.assertEqual(health_status["service"], "test_service")
        self.assertEqual(health_status["system"]["status"], HealthStatus.HEALTHY)
        self.assertEqual(health_status["system"]["cpu_percent"], 50.0)
        self.assertEqual(health_status["system"]["memory_percent"], 60.0)
        self.assertEqual(health_status["system"]["disk_percent"], 70.0)
        self.assertEqual(health_status["dependencies"]["status"], HealthStatus.HEALTHY)
        self.assertEqual(len(health_status["dependencies"]["items"]), 1)
        self.assertEqual(health_status["dependencies"]["items"][0]["name"], "database")
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.HEALTHY
        )

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_degraded_system(
        self, mock_disk_usage: Any, mock_virtual_memory: Any, mock_cpu_percent: Any
    ) -> Any:
        """Test that HealthCheck returns degraded status when system metrics exceed thresholds"""
        mock_cpu_percent.return_value = 95.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)
        health_check = HealthCheck(service_name="test_service")

        def check_database():
            return DependencyStatus(
                name="database", status=HealthStatus.HEALTHY, details={"latency_ms": 10}
            )

        health_check.add_dependency_check(check_database)
        health_status = health_check.check_health()
        self.assertEqual(health_status["status"], HealthStatus.DEGRADED)
        self.assertEqual(health_status["system"]["status"], HealthStatus.DEGRADED)
        self.assertEqual(health_status["dependencies"]["status"], HealthStatus.HEALTHY)

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_degraded_dependency(
        self, mock_disk_usage: Any, mock_virtual_memory: Any, mock_cpu_percent: Any
    ) -> Any:
        """Test that HealthCheck returns degraded status when a dependency is degraded"""
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)
        health_check = HealthCheck(service_name="test_service")

        def check_database():
            return DependencyStatus(
                name="database",
                status=HealthStatus.DEGRADED,
                details={"latency_ms": 500},
            )

        health_check.add_dependency_check(check_database)
        health_status = health_check.check_health()
        self.assertEqual(health_status["status"], HealthStatus.DEGRADED)
        self.assertEqual(health_status["system"]["status"], HealthStatus.HEALTHY)
        self.assertEqual(health_status["dependencies"]["status"], HealthStatus.DEGRADED)
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.DEGRADED
        )

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_unhealthy_dependency(
        self, mock_disk_usage: Any, mock_virtual_memory: Any, mock_cpu_percent: Any
    ) -> Any:
        """Test that HealthCheck returns unhealthy status when a dependency is unhealthy"""
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)
        health_check = HealthCheck(service_name="test_service")

        def check_database():
            return DependencyStatus(
                name="database",
                status=HealthStatus.UNHEALTHY,
                details={"error": "Connection refused"},
            )

        health_check.add_dependency_check(check_database)
        health_status = health_check.check_health()
        self.assertEqual(health_status["status"], HealthStatus.UNHEALTHY)
        self.assertEqual(health_status["system"]["status"], HealthStatus.HEALTHY)
        self.assertEqual(
            health_status["dependencies"]["status"], HealthStatus.UNHEALTHY
        )
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.UNHEALTHY
        )

    @patch("src.utils.health_check.psutil.cpu_percent")
    @patch("src.utils.health_check.psutil.virtual_memory")
    @patch("src.utils.health_check.psutil.disk_usage")
    def test_health_check_dependency_exception(
        self, mock_disk_usage: Any, mock_virtual_memory: Any, mock_cpu_percent: Any
    ) -> Any:
        """Test that HealthCheck handles exceptions in dependency checks"""
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = Mock(percent=60.0)
        mock_disk_usage.return_value = Mock(percent=70.0)
        health_check = HealthCheck(service_name="test_service")

        def check_database():
            raise Exception("Unexpected error")

        health_check.add_dependency_check(check_database)
        health_status = health_check.check_health()
        self.assertEqual(health_status["status"], HealthStatus.UNHEALTHY)
        self.assertEqual(
            health_status["dependencies"]["status"], HealthStatus.UNHEALTHY
        )
        self.assertEqual(health_status["dependencies"]["items"][0]["name"], "unknown")
        self.assertEqual(
            health_status["dependencies"]["items"][0]["status"], HealthStatus.UNHEALTHY
        )
        self.assertEqual(
            health_status["dependencies"]["items"][0]["details"]["error"],
            "Unexpected error",
        )

    def test_add_health_check_endpoints(self) -> Any:
        """Test that add_health_check_endpoints adds the correct endpoints to a FastAPI app"""
        app = FastAPI()
        health_check = HealthCheck(service_name="test_service")
        add_health_check_endpoints(app, health_check)
        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
        response = client.get("/health/liveness")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
        health_check.check_health = Mock(return_value={"status": HealthStatus.HEALTHY})
        response = client.get("/health/readiness")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": HealthStatus.HEALTHY})
        response = client.get("/health/detailed")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": HealthStatus.HEALTHY})
        health_check.check_health = Mock(
            return_value={"status": HealthStatus.UNHEALTHY}
        )
        response = client.get("/health/readiness")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": HealthStatus.UNHEALTHY})
        response = client.get("/health/detailed")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": HealthStatus.UNHEALTHY})


if __name__ == "__main__":
    unittest.main()
