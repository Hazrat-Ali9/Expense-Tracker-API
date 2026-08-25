from fastapi.testclient import TestClient


def create_transaction(
    client: TestClient, headers: dict[str, str], payload: dict[str, object]
) -> dict[str, object]:
    response = client.post("/transactions", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_create_transaction(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, object],
) -> None:
    transaction = create_transaction(client, auth_headers, transaction_payload)

    assert transaction["title"] == "Groceries"
    assert transaction["amount"] == 1250.50
    assert transaction["owner_id"] == 1


def test_get_transactions(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, object],
) -> None:
    create_transaction(client, auth_headers, transaction_payload)
    second_payload = {
        **transaction_payload,
        "title": "Salary",
        "amount": 50000,
        "type": "income",
        "category": "Work",
    }
    create_transaction(client, auth_headers, second_payload)

    response = client.get("/transactions", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {item["type"] for item in response.json()} == {"income", "expense"}


def test_get_specific_transaction_and_enforce_ownership(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, object],
) -> None:
    transaction = create_transaction(client, auth_headers, transaction_payload)

    response = client.get(f"/transactions/{transaction['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == transaction["id"]

    client.post(
        "/auth/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "secure-password",
        },
    )
    login = client.post(
        "/auth/login", data={"username": "bob", "password": "secure-password"}
    )
    bob_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    forbidden = client.get(
        f"/transactions/{transaction['id']}", headers=bob_headers
    )
    assert forbidden.status_code == 404
    assert forbidden.json()["detail"] == "Transaction not found"


def test_update_transaction(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, object],
) -> None:
    transaction = create_transaction(client, auth_headers, transaction_payload)

    response = client.put(
        f"/transactions/{transaction['id']}",
        json={"title": "Monthly groceries", "amount": 1400},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Monthly groceries"
    assert response.json()["amount"] == 1400
    assert response.json()["category"] == "Food"


def test_delete_transaction(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, object],
) -> None:
    transaction = create_transaction(client, auth_headers, transaction_payload)

    response = client.delete(
        f"/transactions/{transaction['id']}", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Transaction deleted successfully"}
    assert (
        client.get(f"/transactions/{transaction['id']}", headers=auth_headers).status_code
        == 404
    )


def test_filter_transactions(
    client: TestClient,
    auth_headers: dict[str, str],
    transaction_payload: dict[str, object],
) -> None:
    create_transaction(client, auth_headers, transaction_payload)
    create_transaction(
        client,
        auth_headers,
        {
            **transaction_payload,
            "title": "Bus fare",
            "amount": 80,
            "category": "Transport",
        },
    )

    response = client.get(
        "/transactions/filter",
        params={"type": "expense", "category": "food", "minimum_amount": 100},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Groceries"]

