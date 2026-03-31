from typing import Any, Dict

from core.health_check import (
    check_database_connections,
    check_feature_store_connection,
    check_model_versions,
)
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "api_status": "ok",
        "feature_store": check_feature_store_connection(),
        "model_cache": check_model_versions(),
        "db_connections": check_database_connections(),
    }


@router.get("/ready")
def readiness_probe() -> Dict[str, str]:
    return {"status": "ready"}
