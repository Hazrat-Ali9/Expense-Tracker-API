# Expense Tracker API

A production-ready personal expense tracker built with FastAPI, SQLAlchemy,
PostgreSQL, Pydantic, and JWT authentication. Every transaction query is scoped
to the authenticated user, preventing users from viewing or changing another
user's data.

## Features

- User registration with Argon2 password hashing
- OAuth2-compatible login with expiring JWT access tokens
- Create, list, read, update, and delete income or expense transactions
- Filter by transaction type, category, minimum amount, and maximum amount
- Pydantic request validation plus database-level integrity constraints
- Interactive OpenAPI documentation at `/docs`
- Six pytest cases covering the required CRUD lifecycle, filtering, and ownership
- Docker Compose development environment and Render Blueprint deployment

## API endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| `POST` | `/auth/register` | Register a user | No |
| `POST` | `/auth/login` | Receive a bearer token | No |
| `POST` | `/transactions` | Create a transaction | Yes |
| `GET` | `/transactions` | List the current user's transactions | Yes |
| `GET` | `/transactions/filter` | Filter the current user's transactions | Yes |
| `GET` | `/transactions/{id}` | Read one owned transaction | Yes |
| `PUT` | `/transactions/{id}` | Update one owned transaction | Yes |
| `DELETE` | `/transactions/{id}` | Delete one owned transaction | Yes |

Supported filter query parameters are `type`, `category`, `minimum_amount`, and
`maximum_amount`. For example:

```text
/transactions/filter?type=expense&category=Food&minimum_amount=100
```

## Run with Docker

Docker Compose starts both the API and PostgreSQL:

```bash
docker compose up --build
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to register, log
in, authorize with the returned token, and exercise every endpoint.

## Run locally

Prerequisites: Python 3.12+ and a PostgreSQL database.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Update `DATABASE_URL` and `JWT_SECRET_KEY` in `.env` before starting the API.
Tables are created automatically when the application starts.

## Authentication example

Register:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"alice@example.com","password":"secure-password"}'
```

Log in (the endpoint accepts OAuth2 form data):

```bash
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=alice&password=secure-password'
```

Pass the returned token as `Authorization: Bearer <token>` on all transaction
requests.

## Tests

Tests use an isolated SQLite database, while the application itself defaults to
PostgreSQL.

```bash
pytest -q
```

## Deploy to Render

The included `render.yaml` defines a web service and managed PostgreSQL database.

1. In Render, choose **New → Blueprint**.
2. Connect this GitHub repository.
3. Confirm the resources from `render.yaml` and deploy.
4. Open the deployed `/docs` path to verify the API.

Render generates the production JWT secret and supplies the managed database URL
automatically. The app normalizes Render's PostgreSQL URL for the Psycopg 3 driver.

## Project structure

```text
app/
├── api/deps.py             # Database and current-user dependencies
├── core/                   # Settings and security helpers
├── models/                 # SQLAlchemy tables and relationships
├── routers/                # Authentication and transaction endpoints
├── schemas/                # Pydantic request/response models
├── database.py             # Engine, session, and declarative base
└── main.py                 # FastAPI application
tests/                      # Pytest API tests
```

