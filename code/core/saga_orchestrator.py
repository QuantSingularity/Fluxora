import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

import requests
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SagaState(Enum):
    STARTED = "STARTED"
    EXECUTING = "EXECUTING"
    COMPENSATING = "COMPENSATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class StepState(Enum):
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"


class SagaStep(BaseModel):
    id: str
    service_name: str
    action_endpoint: str
    compensation_endpoint: str
    state: StepState
    payload: Dict
    result: Optional[Dict] = None


class Saga(BaseModel):
    id: str
    name: str
    state: SagaState
    steps: List[SagaStep]
    current_step_index: int
    created_at: float
    updated_at: float


# In-memory storage for demonstration
# In production, use a persistent database
sagas: Dict[str, Saga] = {}

app = FastAPI(title="Saga Orchestrator")


@app.post("/sagas")
async def create_saga(name: str, steps: List[Dict], background_tasks: BackgroundTasks):
    """
    Create a new saga with the specified steps
    """
    saga_id = str(uuid.uuid4())

    saga_steps = []
    for i, step_data in enumerate(steps):
        step = SagaStep(
            id=f"{saga_id}-step-{i}",
            service_name=step_data["service_name"],
            action_endpoint=step_data["action_endpoint"],
            compensation_endpoint=step_data["compensation_endpoint"],
            state=StepState.PENDING,
            payload=step_data["payload"],
        )
        saga_steps.append(step)

    saga = Saga(
        id=saga_id,
        name=name,
        state=SagaState.STARTED,
        steps=saga_steps,
        current_step_index=0,
        created_at=time.time(),
        updated_at=time.time(),
    )

    sagas[saga_id] = saga

    # Start saga execution in background
    background_tasks.add_task(execute_saga, saga_id)

    return {"saga_id": saga_id, "state": saga.state.value}


@app.get("/sagas/{saga_id}")
async def get_saga(saga_id: str) -> Dict[str, Any]:
    """
    Get saga details
    """
    if saga_id not in sagas:
        raise HTTPException(status_code=404, detail="Saga not found")

    saga = sagas[saga_id]
    return {
        "saga_id": saga.id,
        "name": saga.name,
        "state": saga.state.value,
        "steps": [
            {
                "id": step.id,
                "service_name": step.service_name,
                "state": step.state.value,
                "result": step.result,
            }
            for step in saga.steps
        ],
        "current_step_index": saga.current_step_index,
        "created_at": saga.created_at,
        "updated_at": saga.updated_at,
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    """
    return {"status": "healthy"}


async def execute_saga(saga_id: str):
    """
    Execute the saga steps in sequence
    """
    saga = sagas[saga_id]
    saga.state = SagaState.EXECUTING

    while saga.current_step_index < len(saga.steps):
        step = saga.steps[saga.current_step_index]
        step.state = StepState.EXECUTING

        try:
            # Get service URL from service registry
            service_url = get_service_url(step.service_name)
            if not service_url:
                step.state = StepState.FAILED
                await compensate_saga(saga_id)
                return

            # Execute step action
            response = requests.post(
                f"{service_url}{step.action_endpoint}", json=step.payload
            )

            if response.status_code == 200:
                step.state = StepState.EXECUTED
                step.result = response.json()
                saga.current_step_index += 1
            else:
                step.state = StepState.FAILED
                await compensate_saga(saga_id)
                return
        except Exception as e:
            logger.info(f"Error executing step {step.id}: {str(e)}")
            step.state = StepState.FAILED
            await compensate_saga(saga_id)
            return

        saga.updated_at = time.time()

    # All steps executed successfully
    saga.state = SagaState.COMPLETED
    saga.updated_at = time.time()


async def compensate_saga(saga_id: str) -> None:
    """
    Compensate the saga by executing compensation steps in reverse order
    """
    saga = sagas[saga_id]
    saga.state = SagaState.COMPENSATING

    for i in range(saga.current_step_index - 1, -1, -1):
        step = saga.steps[i]
        if step.state == StepState.EXECUTED:
            step.state = StepState.COMPENSATING

            try:
                # Get service URL from service registry
                service_url = get_service_url(step.service_name)
                if not service_url:
                    step.state = StepState.FAILED
                    continue

                # Execute step compensation
                response = requests.post(
                    f"{service_url}{step.compensation_endpoint}",
                    json={"step_id": step.id, "original_payload": step.payload},
                )

                if response.status_code == 200:
                    step.state = StepState.COMPENSATED
                else:
                    step.state = StepState.FAILED
            except Exception as e:
                logger.info(f"Error compensating step {step.id}: {str(e)}")
                step.state = StepState.FAILED

            saga.updated_at = time.time()

    saga.state = SagaState.FAILED
    saga.updated_at = time.time()


def get_service_url(service_name: str) -> Optional[str]:
    """
    Get service URL from service registry
    """
    try:
        registry_url = "http://service-registry:8500"
        response = requests.get(f"{registry_url}/v1/catalog/service/{service_name}")
        if response.status_code == 200:
            services = response.json()
            if services:
                service = services[0]
                return f"http://{service['ServiceAddress']}:{service['ServicePort']}"
        return None
    except Exception as e:
        logger.info(f"Error getting service URL: {str(e)}")
        return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
