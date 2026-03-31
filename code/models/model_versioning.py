from datetime import datetime
from typing import Any

from mlflow.tracking import MlflowClient


def promote_model_to_production(run_id: Any) -> Any:
    client = MlflowClient()
    current_prod = client.get_latest_versions("EnergyModel", stages=["Production"])
    for mv in current_prod:
        client.transition_model_version_stage(
            name="EnergyModel", version=mv.version, stage="Archived"
        )
    client.transition_model_version_stage(
        name="EnergyModel", version=run_id, stage="Production"
    )
    client.update_model_version(
        name="EnergyModel",
        version=run_id,
        description=f"Promoted via CI/CD pipeline at {datetime.now()}",
    )
