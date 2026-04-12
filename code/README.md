# Fluxora

Energy data management and ML-powered consumption prediction platform.

## Project Structure

```
fluxora/
├── backend/          # FastAPI REST API
│   ├── app/
│   │   ├── api/v1/   # Route handlers (auth, data, analytics, predictions)
│   │   ├── core/     # Security, config, circuit-breaker, retry, fallback, middleware
│   │   ├── crud/     # Database CRUD helpers
│   │   ├── db/       # SQLAlchemy engine & session factory
│   │   ├── models/   # ORM models
│   │   └── schemas/  # Pydantic schemas
│   ├── migrations/   # Alembic database migrations
│   ├── tests/        # pytest suite (api / integration / unit)
│   ├── main.py       # Uvicorn entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── ml_core/          # Machine-learning package (framework-independent)
    ├── __init__.py
    ├── data_validator.py      # DataFrame validation helpers
    ├── feature_engineering.py # Time-series, lag, rolling features
    ├── temporal_features.py   # Cyclical & calendar features
    ├── training.py            # RandomForest training pipeline
    └── requirements.txt
```

## Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, etc.
```

### 3. Run database migrations

```bash
cd backend
alembic upgrade head
```

### 4. Start the API server

```bash
cd backend
python main.py
# or
uvicorn app.main:app --reload
```

API docs available at http://localhost:8000/docs

### 5. Run tests

```bash
cd backend
pytest
```

## ml_core Package

`ml_core` is intentionally framework-independent – it depends only on
`numpy`, `pandas`, `scikit-learn`, and `joblib`. It can be imported by
external pipelines, notebooks, or batch jobs without pulling in FastAPI or
SQLAlchemy.

The backend's `app/main.py` and `backend/main.py` both insert the project
root into `sys.path` so `ml_core` is discoverable at runtime. When running
pytest from `backend/`, `tests/conftest.py` performs the same insertion.

## Key Fixes Applied

| Area                | Fix                                                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `predictions.py`    | Rewrote iterative prediction loop — lag features now reference the correct previous step, and time features use the actual future timestamp |
| `analytics.py`      | Replaced broken efficiency formula (`100 − kwh/temp`) with a properly normalised score `100 × (1 − kwh/max_kwh)`                            |
| `retry.py`          | Removed redundant `import time as time` self-alias                                                                                          |
| `training.py`       | Replaced deprecated `np.random.normal` global call with `np.random.default_rng(seed=42)` for reproducibility                                |
| `migrations/env.py` | Added `sys.path` guard so Alembic resolves `app.*` regardless of working directory                                                          |
| All imports         | Updated every `from app.services.*` reference to `from ml_core.*` across source and tests                                                   |
