import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


def promote_model_to_production(run_id: Any) -> Any:
    """
    Promotes a specific model version to production in MLflow.
    Falls back gracefully if MLflow is not installed.
    """
    try:
        from mlflow.tracking import MlflowClient

        client = MlflowClient()
        current_prod = client.get_latest_versions("EnergyModel", stages=["Production"])
        for mv in current_prod:
            client.transition_model_version_stage(
                name="EnergyModel", version=mv.version, stage="Archived"
            )
        client.transition_model_version_stage(
            name="EnergyModel", version=str(run_id), stage="Production"
        )
        client.update_model_version(
            name="EnergyModel",
            version=str(run_id),
            description=f"Promoted via CI/CD pipeline at {datetime.now()}",
        )
        logger.info(f"Model version {run_id} promoted to Production.")
        return {"status": "promoted", "version": run_id}
    except ImportError:
        logger.warning("MLflow not installed. Skipping model promotion.")
        return {"status": "skipped", "reason": "mlflow not installed"}
    except Exception as e:
        logger.error(f"Failed to promote model version {run_id}: {e}")
        raise


def get_production_model_version() -> Optional[str]:
    """
    Returns the current production model version from MLflow,
    or None if MLflow is unavailable.
    """
    try:
        from mlflow.tracking import MlflowClient

        client = MlflowClient()
        versions = client.get_latest_versions("EnergyModel", stages=["Production"])
        if versions:
            return versions[0].version
        return None
    except ImportError:
        logger.warning("MLflow not installed.")
        return None
    except Exception as e:
        logger.error(f"Error fetching production model version: {e}")
        return None
