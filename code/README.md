# Fluxora – Energy Data Management & Prediction API

A FastAPI-based backend for collecting, storing, analysing, and forecasting energy consumption data.

---

## Features

| Area              | Details                                                                      |
| ----------------- | ---------------------------------------------------------------------------- |
| **Auth**          | JWT-based registration & login (`/v1/auth`)                                  |
| **Data**          | CRUD for energy readings with time-range queries (`/v1/data`)                |
| **Predictions**   | ML-driven hourly consumption forecasts (`/v1/predictions`)                   |
| **Analytics**     | Aggregated weekly / monthly / yearly reports (`/v1/analytics`)               |
| **ML Pipeline**   | RandomForest training, feature engineering, lag/rolling features             |
| **Resilience**    | Circuit breaker, exponential-backoff retry, fallback strategies              |
| **Observability** | Prometheus metrics, structured error responses, request logging              |
| **Migrations**    | Alembic database migrations                                                  |
| **Docker**        | Multi-stage Dockerfile + docker-compose (API, Postgres, Prometheus, Grafana) |
| **Tests**         | pytest suite with in-memory SQLite fixtures                                  |

---

## Quick Start (local)

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd fluxora

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the app
cp .env.example .env
# Edit .env – at minimum set SECRET_KEY to a strong random value:
python -c "import secrets; print(secrets.token_hex(32))"

# 5. Start the server
./start.sh
# or: python -m uvicorn main:app --reload
```

API docs are available at **http://localhost:8000/docs**

---

## Docker

### Production (PostgreSQL + monitoring)

```bash
cp .env.example .env   # edit as needed
docker compose up -d
```

### Development (SQLite, hot-reload)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### With monitoring stack

```bash
docker compose --profile monitoring up -d
# Grafana → http://localhost:3001  (admin / admin)
# Prometheus → http://localhost:9091
```

---

## API Endpoints

### Auth

| Method | Path                | Description         |
| ------ | ------------------- | ------------------- |
| `POST` | `/v1/auth/register` | Register a new user |
| `POST` | `/v1/auth/token`    | Obtain a JWT token  |

### Data

| Method | Path             | Description               |
| ------ | ---------------- | ------------------------- |
| `POST` | `/v1/data/`      | Record energy reading     |
| `GET`  | `/v1/data/`      | List readings (paginated) |
| `GET`  | `/v1/data/query` | Query by time range       |

### Predictions

| Method | Path                      | Description                        |
| ------ | ------------------------- | ---------------------------------- |
| `GET`  | `/v1/predictions/?days=7` | Forecast next N days               |
| `POST` | `/v1/predictions/train`   | Trigger model training (superuser) |

### Analytics

| Method | Path                          | Description                            |
| ------ | ----------------------------- | -------------------------------------- |
| `GET`  | `/v1/analytics/?period=month` | Aggregated analytics (week/month/year) |
| `GET`  | `/v1/analytics/summary`       | 30-day summary                         |

### System

| Method | Path      | Description            |
| ------ | --------- | ---------------------- |
| `GET`  | `/health` | Liveness probe         |
| `GET`  | `/`       | API info               |
| `GET`  | `/docs`   | Interactive Swagger UI |

---

## Database Migrations (Alembic)

```bash
# Generate a new migration after changing models
alembic revision --autogenerate -m "describe change"

# Apply migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

---

## Running Tests

```bash
pip install -r requirements.txt
pytest -v
```

---

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable       | Default                  | Description             |
| -------------- | ------------------------ | ----------------------- |
| `DATABASE_URL` | `sqlite:///./fluxora.db` | SQLAlchemy DB URL       |
| `SECRET_KEY`   | _(must be set)_          | JWT signing key         |
| `API_PORT`     | `8000`                   | Server port             |
| `API_WORKERS`  | `1`                      | Uvicorn workers         |
| `MODEL_PATH`   | `./fluxora_model.joblib` | Saved model path        |
| `METRICS_PORT` | `9090`                   | Prometheus metrics port |
| `LOG_LEVEL`    | `INFO`                   | Logging verbosity       |

---

## Project Structure

```
code/
├── api/v1/             # Route handlers (auth, data, predictions, analytics)
├── backend/            # App factory, DB session, security, middleware
├── core/               # Circuit breaker, retry, config, metrics, tracing
├── crud/               # Database access layer
├── data/               # Feature engineering & dataset generation
├── features/           # Feature pipeline & feature store
├── migrations/         # Alembic migration scripts
├── models/             # SQLAlchemy ORM models + ML train/predict
├── schemas/            # Pydantic request/response schemas
├── tests/              # pytest test suite
├── docker/             # Prometheus & Grafana config
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── requirements.txt
└── main.py
```
