from typing import Any

from api.v1 import analytics, auth, data, predictions
from backend.database import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize database
init_db()

app = FastAPI(
    title="Fluxora API",
    description="API for energy data management and prediction.",
    version="1.0.0",
)

# Configure CORS
origins = ["http://localhost", "http://localhost:3000", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/v1")
app.include_router(data.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")
app.include_router(predictions.router, prefix="/v1")


@app.get("/health", tags=["system"])
def health_check() -> Any:
    """Basic health check endpoint"""
    return {"status": "ok"}


@app.get("/", tags=["system"])
def root() -> Any:
    """Root endpoint"""
    return {
        "message": "Fluxora API",
        "version": "1.0.0",
        "docs": "/docs",
    }
