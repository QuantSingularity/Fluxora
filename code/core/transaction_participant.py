from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class TransactionRequest(BaseModel):
    transaction_id: str


def add_transaction_endpoints(app: FastAPI, resource_manager: Any) -> None:
    """
    Add transaction participant endpoints to the FastAPI application
    """

    @app.post("/transaction/prepare")
    async def prepare_transaction(request: TransactionRequest):
        """
        Prepare resources for the transaction
        """
        try:
            resource_manager.prepare(request.transaction_id)
            return {"status": "prepared"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/transaction/commit")
    async def commit_transaction(request: TransactionRequest):
        """
        Commit the prepared transaction
        """
        try:
            resource_manager.commit(request.transaction_id)
            return {"status": "committed"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/transaction/abort")
    async def abort_transaction(request: TransactionRequest):
        """
        Abort the transaction
        """
        try:
            resource_manager.abort(request.transaction_id)
            return {"status": "aborted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
