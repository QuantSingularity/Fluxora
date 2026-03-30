import asyncio
import json
import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./outbox.db"  # Use PostgreSQL in production
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id = Column(String, primary_key=True, index=True)
    destination_service = Column(String, index=True)
    payload = Column(Text)
    created_at = Column(Float)
    processed = Column(Boolean, default=False)
    processed_at = Column(Float, nullable=True)
    retry_count = Column(Integer, default=0)


# Create tables
Base.metadata.create_all(bind=engine)


class MessageStatus(Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class OutboxMessageModel(BaseModel):
    destination_service: str
    payload: Dict


app = FastAPI(title="Outbox Service")


@app.post("/messages")
async def create_message(message: OutboxMessageModel) -> Dict[str, Any]:
    """
    Create a new outbox message
    """
    db = SessionLocal()
    try:
        message_id = str(uuid.uuid4())
        db_message = OutboxMessage(
            id=message_id,
            destination_service=message.destination_service,
            payload=json.dumps(message.payload),
            created_at=time.time(),
            processed=False,
            processed_at=None,
            retry_count=0,
        )
        db.add(db_message)
        db.commit()
        return {"message_id": message_id, "status": MessageStatus.PENDING.value}
    finally:
        db.close()


@app.get("/messages/{message_id}")
async def get_message(message_id: str) -> Dict[str, Any]:
    """
    Get message details
    """
    db = SessionLocal()
    try:
        message = db.query(OutboxMessage).filter(OutboxMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return {
            "message_id": message.id,
            "destination_service": str(message.destination_service),
            "payload": json.loads(str(message.payload)),
            "created_at": message.created_at,
            "processed": message.processed,
            "processed_at": message.processed_at,
            "retry_count": message.retry_count,
            "status": (
                MessageStatus.DELIVERED.value
                if message.processed
                else MessageStatus.PENDING.value
            ),
        }
    finally:
        db.close()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    """
    return {"status": "healthy"}


@app.on_event("startup")
async def start_message_processor() -> None:
    """
    Start the background message processor
    """
    asyncio.create_task(process_messages())


async def process_messages() -> None:
    """
    Process pending outbox messages
    """
    while True:
        try:
            db = SessionLocal()
            # Get unprocessed messages
            messages = (
                db.query(OutboxMessage)
                .filter(not OutboxMessage.processed)
                .order_by(OutboxMessage.created_at)
                .limit(10)
                .all()
            )

            for message in messages:
                try:
                    # Get service URL from service registry
                    service_url = get_service_url(str(message.destination_service))
                    if not service_url:
                        continue

                    # Send message to destination service
                    payload_data = json.loads(str(message.payload))
                    response = requests.post(
                        f"{service_url}/messages", json=payload_data
                    )

                    if response.status_code == 200:
                        # Mark message as processed
                        message.processed = True  # type: ignore[assignment]
                        message.processed_at = time.time()  # type: ignore[assignment]
                    else:
                        # Increment retry count
                        message.retry_count += 1  # type: ignore[assignment]
                except Exception as e:
                    logger.info(f"Error processing message {message.id}: {str(e)}")
                    message.retry_count += 1  # type: ignore[assignment]

            db.commit()
        except Exception as e:
            logger.info(f"Error in message processor: {str(e)}")
        finally:
            db.close()

        # Sleep before next processing cycle
        await asyncio.sleep(1)


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
