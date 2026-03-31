import json
import logging
import os
from typing import Any, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ResourceManager:

    def __init__(self, resource_type: str) -> None:
        self.resource_type = resource_type
        self.prepared_resources: Dict[str, Dict[str, Any]] = {}
        self.temp_dir = "/tmp/transactions"
        os.makedirs(self.temp_dir, exist_ok=True)

    def prepare(
        self,
        transaction_id: str,
        resource_id: str,
        operation: str,
        data: Dict[str, Any],
    ) -> Any:
        """
        Prepare a resource for a transaction
        """
        resource_key = f"{transaction_id}:{resource_id}"
        self.prepared_resources[resource_key] = {"operation": operation, "data": data}
        self._persist_prepared_state(transaction_id, resource_id, operation, data)
        return True

    def commit(self, transaction_id: str) -> Any:
        """
        Commit all prepared resources for the transaction
        """
        resources_to_commit = {
            k: v
            for k, v in self.prepared_resources.items()
            if k.startswith(f"{transaction_id}:")
        }
        for resource_key, resource_data in resources_to_commit.items():
            try:
                self._execute_operation(
                    resource_data["operation"], resource_data["data"]
                )
                del self.prepared_resources[resource_key]
                transaction_id, resource_id = resource_key.split(":", 1)
                self._remove_persisted_state(transaction_id, resource_id)
            except Exception as e:
                logger.info(f"Error committing resource {resource_key}: {str(e)}")
        return True

    def abort(self, transaction_id: str) -> Any:
        """
        Abort all prepared resources for the transaction
        """
        resources_to_abort = {
            k: v
            for k, v in self.prepared_resources.items()
            if k.startswith(f"{transaction_id}:")
        }
        for resource_key, resource_data in resources_to_abort.items():
            try:
                del self.prepared_resources[resource_key]
                transaction_id, resource_id = resource_key.split(":", 1)
                self._remove_persisted_state(transaction_id, resource_id)
            except Exception as e:
                logger.info(f"Error aborting resource {resource_key}: {str(e)}")
        return True

    def _execute_operation(self, operation: str, data: Dict[str, Any]) -> Any:
        """
        Execute the operation on the resource
        This is a mock implementation for demonstration
        In production, this would interact with actual resources (database, file system, etc.)
        """
        if operation == "create":
            logger.info(f"Creating {self.resource_type} with data: {data}")
            # In production: perform actual resource creation
            return {
                "status": "created",
                "resource_type": self.resource_type,
                "data": data,
            }
        elif operation == "update":
            logger.info(f"Updating {self.resource_type} with data: {data}")
            # In production: perform actual resource update
            return {
                "status": "updated",
                "resource_type": self.resource_type,
                "data": data,
            }
        elif operation == "delete":
            logger.info(f"Deleting {self.resource_type} with data: {data}")
            # In production: perform actual resource deletion
            return {
                "status": "deleted",
                "resource_type": self.resource_type,
                "data": data,
            }
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def _persist_prepared_state(
        self,
        transaction_id: str,
        resource_id: str,
        operation: str,
        data: Dict[str, Any],
    ) -> Any:
        """
        Persist the prepared state to disk for recovery
        """
        transaction_dir = os.path.join(self.temp_dir, transaction_id)
        os.makedirs(transaction_dir, exist_ok=True)
        resource_file = os.path.join(transaction_dir, f"{resource_id}.json")
        with open(resource_file, "w") as f:
            json.dump({"operation": operation, "data": data}, f)

    def _remove_persisted_state(self, transaction_id: str, resource_id: str) -> Any:
        """
        Remove the persisted state from disk
        """
        resource_file = os.path.join(
            self.temp_dir, transaction_id, f"{resource_id}.json"
        )
        if os.path.exists(resource_file):
            os.remove(resource_file)
        transaction_dir = os.path.join(self.temp_dir, transaction_id)
        if os.path.exists(transaction_dir) and (not os.listdir(transaction_dir)):
            os.rmdir(transaction_dir)
