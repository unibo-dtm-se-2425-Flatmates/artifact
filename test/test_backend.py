import sqlite3
from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.db.database import Database


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create a fresh in-memory-style database per test and patch routers to use it."""
    db_instance = Database()
    db_instance.conn.close()

    db_path = tmp_path / "test.db"
    db_instance.conn = sqlite3.connect(db_path, check_same_thread=False)
    db_instance.conn.row_factory = sqlite3.Row
    db_instance._ensure_tables()

    targets = [
        "backend.db.database",
        "backend.db",
        "backend.routers.calendar",
        "backend.routers.shopping",
        "backend.routers.expenses",
        "backend.routers.house",
    ]
    for target in targets:
        monkeypatch.setattr(f"{target}.db", db_instance)

    yield db_instance

    db_instance.conn.close()


@pytest.fixture
def client(test_db):
    return TestClient(app)


def test_root_returns_welcome(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Flatmate App API"}


def test_calendar_flow(client):
    event_payload = {
        "title": "Test Event",
        "date": str(date.today()),
        "description": "Sample",
        "assigned_to": ["Alice"],
    }
    create_resp = client.post("/calendar/", json=event_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["id"] is not None

    list_resp = client.get("/calendar/")
    events = list_resp.json()
    assert len(events) == 1
    assert events[0]["title"] == event_payload["title"]

    update_payload = {
        "title": "Updated Event",
        "date": event_payload["date"],
        "description": "Updated description",
        "assigned_to": ["Bob"],
    }
    update_resp = client.put(f"/calendar/{created['id']}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Event"


def test_shopping_flow(client):
    item_payload = {"name": "Milk", "quantity": 2, "added_by": "Alice"}
    create_resp = client.post("/shopping/", json=item_payload)
    assert create_resp.status_code == 200
    item_id = create_resp.json()["id"]

    list_resp = client.get("/shopping/")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["name"] == "Milk"

    delete_resp = client.delete(f"/shopping/{item_id}")
    assert delete_resp.status_code == 200
    assert client.get("/shopping/").json() == []


def test_house_settings(client):
    payload = {"name": "My House", "flatmates": ["Alice", "Bob"]}
    save_resp = client.post("/house/", json=payload)
    assert save_resp.status_code == 200
    assert save_resp.json()["flatmates"] == payload["flatmates"]

    fetch_resp = client.get("/house/")
    assert fetch_resp.status_code == 200
    returned = fetch_resp.json()
    assert returned["name"] == "My House"
    assert returned["flatmates"] == ["Alice", "Bob"]


def test_expenses_and_debts_flow(client):
    expense_payload = {
        "title": "Groceries",
        "amount": 100.0,
        "payer": "Alice",
        "involved_people": ["Alice", "Bob"],
    }
    create_expense = client.post("/expenses/", json=expense_payload)
    assert create_expense.status_code == 200

    debts_resp = client.get("/expenses/debts")
    assert debts_resp.status_code == 200
    debts = debts_resp.json()
    assert len(debts) == 1
    assert debts[0]["debtor"] == "Bob"
    assert debts[0]["creditor"] == "Alice"
    assert debts[0]["amount"] == 50.0

    same_person = client.post(
        "/expenses/reimbursements",
        json={"from_person": "Alice", "to_person": "Alice", "amount": 10},
    )
    assert same_person.status_code == 400

    negative_amount = client.post(
        "/expenses/reimbursements",
        json={"from_person": "Bob", "to_person": "Alice", "amount": -5},
    )
    assert negative_amount.status_code == 400

    reimbursement_payload = {
        "from_person": "Bob",
        "to_person": "Alice",
        "amount": 20.0,
        "note": "Cash",
    }
    reimb_resp = client.post("/expenses/reimbursements", json=reimbursement_payload)
    assert reimb_resp.status_code == 200
    reimbursement = reimb_resp.json()
    assert reimbursement["id"] is not None
    assert reimbursement["note"] == "Cash"

    reimb_list = client.get("/expenses/reimbursements")
    assert reimb_list.status_code == 200
    assert len(reimb_list.json()) == 1

    debts_after = client.get("/expenses/debts")
    assert debts_after.status_code == 200
    updated = debts_after.json()
    assert len(updated) == 1
    assert updated[0]["amount"] == 30.0