import os
from collections.abc import Generator

import pytest


# Configure a disposable SQLite database before importing the application.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./test_expense_tracker.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-validation"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    registration = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secure-password",
        },
    )
    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": "alice", "password": "secure-password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def transaction_payload() -> dict[str, object]:
    return {
        "title": "Groceries",
        "amount": 1250.50,
        "type": "expense",
        "category": "Food",
        "date": "2026-08-24",
    }

