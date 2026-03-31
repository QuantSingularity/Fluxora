import socket
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil
from fastapi import FastAPI, Response, status


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyStatus:
    """
    Status of a dependency
    """

    def __init__(
        self, name: str, status: HealthStatus, details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.name = name
        self.status = status
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        """
        return {"name": self.name, "status": self.status, "details": self.details}


class HealthCheck:
    """
    Health check for a service
    """

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        self.start_time = time.time()
        self.dependency_checks: List[Callable[[], DependencyStatus]] = []

    def add_dependency_check(self, check_func: Callable[[], DependencyStatus]) -> None:
        """
        Add a dependency check
        """
        self.dependency_checks.append(check_func)

    def check_health(self) -> Dict[str, Any]:
        """
        Check service health
        """
        hostname = socket.gethostname()
        uptime = time.time() - self.start_time
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage("/").percent
        cpu_threshold = 90
        memory_threshold = 90
        disk_threshold = 90
        dependencies = []
        dependency_status = HealthStatus.HEALTHY
        for check_func in self.dependency_checks:
            try:
                status = check_func()
                dependencies.append(status.to_dict())
                if status.status == HealthStatus.UNHEALTHY:
                    dependency_status = HealthStatus.UNHEALTHY
                elif (
                    status.status == HealthStatus.DEGRADED
                    and dependency_status != HealthStatus.UNHEALTHY
                ):
                    dependency_status = HealthStatus.DEGRADED
            except Exception as e:
                dependencies.append(
                    {
                        "name": "unknown",
                        "status": HealthStatus.UNHEALTHY,
                        "details": {"error": str(e)},
                    }
                )
                dependency_status = HealthStatus.UNHEALTHY
        system_status = HealthStatus.HEALTHY
        if (
            cpu_percent >= cpu_threshold
            or memory_percent >= memory_threshold
            or disk_percent >= disk_threshold
        ):
            system_status = HealthStatus.DEGRADED
        overall_status = HealthStatus.HEALTHY
        if (
            system_status == HealthStatus.DEGRADED
            or dependency_status == HealthStatus.DEGRADED
        ):
            overall_status = HealthStatus.DEGRADED
        if dependency_status == HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.UNHEALTHY
        return {
            "status": overall_status,
            "service": self.service_name,
            "hostname": hostname,
            "uptime": uptime,
            "system": {
                "status": system_status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
            },
            "dependencies": {"status": dependency_status, "items": dependencies},
        }


def add_health_check_endpoints(app: FastAPI, health_check: HealthCheck) -> None:
    """
    Add health check endpoints to the FastAPI application
    """

    @app.get("/health")
    async def health() -> Dict[str, str]:
        """
        Basic health check endpoint
        """
        return {"status": "healthy"}

    @app.get("/health/liveness")
    async def liveness() -> Dict[str, str]:
        """
        Liveness probe endpoint
        """
        return {"status": "healthy"}

    @app.get("/health/readiness")
    async def readiness(response: Response) -> Dict[str, Any]:
        """
        Readiness probe endpoint
        """
        health_status = health_check.check_health()
        if health_status["status"] == HealthStatus.UNHEALTHY:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return health_status

    @app.get("/health/detailed")
    async def detailed_health(response: Response) -> Dict[str, Any]:
        """
        Detailed health check endpoint
        """
        health_status = health_check.check_health()
        if health_status["status"] == HealthStatus.UNHEALTHY:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return health_status


def check_feature_store_connection() -> str:
    """Mock check for feature store connection."""
    return "ok"


def check_model_versions() -> str:
    """Mock check for model versions in cache."""
    return "ok"


def check_database_connections() -> str:
    """Mock check for database connections."""
    return "ok"
