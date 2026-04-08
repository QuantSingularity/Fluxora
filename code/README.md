# Fluxora API

Energy data management and prediction API built with FastAPI.

## Project Structure

```
fluxora/
├── app/
│   ├── api/
│   │   └── v1/             # Route handlers
│   │       ├── auth.py     # Authentication endpoints
│   │       ├── data.py     # Energy data CRUD endpoints
│   │       ├── analytics.py
│   │       └── predictions.py
│   ├── core/               # Core utilities
│   │   ├── security.py     # JWT auth, password hashing
│   │   ├── config.py       # Configuration loader
│   │   ├── exceptions.py   # Custom exception classes
│   │   ├── circuit_breaker.py
│   │   ├── retry.py
│   │   ├── fallback.py
│   │   └── error_middleware.py
│   ├── crud/               # Database operations
│   │   ├── user.py
│   │   └── data.py
│   ├── db/                 # Database setup
│   │   ├── database.py
│   │   └── dependencies.py
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── user.py
│   │   └── data.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── user.py
│   │   └── data.py
│   └── services/           # Business logic
│       ├── feature_engineering.py
│       ├── temporal_features.py
│       ├── data_validator.py
│       └── training.py
├── tests/
│   ├── api/                # API endpoint tests
│   ├── integration/        # CRUD + service integration tests
│   └── unit/               # Pure unit tests
├── migrations/             # Alembic migrations
├── main.py                 # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── pytest.ini
```

## Quick Start

```bash
# 1. Create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment file and edit as needed
cp .env.example .env

# 4. Run the API
uvicorn app.main:app --reload

# API docs available at http://localhost:8000/docs
```

## Running Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/auth/register | Register a new user |
| POST | /v1/auth/token | Login (get access + refresh tokens) |
| POST | /v1/auth/refresh | Refresh access token |
| GET | /v1/auth/me | Current user profile |
| POST | /v1/data/ | Create energy record |
| GET | /v1/data/ | List energy records |
| GET | /v1/data/{id} | Get single record |
| PATCH | /v1/data/{id} | Update record |
| DELETE | /v1/data/{id} | Delete record |
| GET | /v1/data/query | Time-range query |
| GET | /v1/analytics/ | Aggregated analytics |
| GET | /v1/analytics/summary | 30-day summary |
| GET | /v1/predictions/ | Consumption forecast |
| POST | /v1/predictions/train | Trigger model training (superuser) |
| GET | /health | Health check |

## Environment Variables

See `.env.example` for all available configuration options.
