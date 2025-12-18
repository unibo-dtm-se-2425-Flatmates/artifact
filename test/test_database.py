import sqlite3
from datetime import date, time

import pytest

from backend.db.database import Database
from backend.models import Event, ShoppingItem, Expense, HouseSettings, Reimbursement


@pytest.fixture
def db_instance(tmp_path):
    instance = Database()
    instance.conn.close()

    db_path = tmp_path / "db.sqlite"
    instance.db_path = db_path
    instance.conn = sqlite3.connect(db_path, check_same_thread=False)
    instance.conn.row_factory = sqlite3.Row
    instance._ensure_tables()

    yield instance

    instance.conn.close()


def test_house_settings_roundtrip(db_instance):
    settings = HouseSettings(name="Test Home", flatmates=["Alice", "Bob"])
    stored = db_instance.update_house_settings(settings)
    assert stored == settings

    retrieved = db_instance.get_house_settings()
    assert retrieved.name == "Test Home"
    assert retrieved.flatmates == ["Alice", "Bob"]


def test_event_crud(db_instance):
    event = Event(
        title="Study Session",
        date=date.today(),
        start_time=time(18, 0),
        end_time=time(20, 0),
        description="Group study",
        assigned_to=["Alice"],
    )
    created = db_instance.add_event(event)
    assert created.id is not None

    events = db_instance.get_events()
    assert len(events) == 1
    assert events[0].title == "Study Session"

    updated_payload = Event(
        title="Updated Session",
        date=event.date,
        start_time=None,
        end_time=None,
        description="Updated",
        assigned_to=["Bob"],
    )
    updated = db_instance.update_event(created.id, updated_payload)
    assert updated is not None
    assert updated.title == "Updated Session"


def test_event_ordering_by_time(db_instance):
    today = date.today()
    early = Event(title="Early", date=today, start_time=time(9, 0), end_time=None, description=None, assigned_to=[])
    mid = Event(title="Mid", date=today, start_time=time(12, 0), end_time=None, description=None, assigned_to=[])
    no_time = Event(title="NoTime", date=today, description=None, assigned_to=[])

    db_instance.add_event(mid)
    db_instance.add_event(no_time)
    db_instance.add_event(early)

    events = db_instance.get_events()
    titles_in_order = [e.title for e in events]
    assert titles_in_order[:3] == ["Early", "Mid", "NoTime"]


def test_shopping_list_flow(db_instance):
    item = ShoppingItem(name="Bread", quantity=2, added_by="Alice")
    created = db_instance.add_shopping_item(item)
    assert created.id is not None

    items = db_instance.get_shopping_list()
    assert len(items) == 1
    assert items[0].name == "Bread"
    assert items[0].purchased is False

    purchased_item = ShoppingItem(name="Milk", quantity=1, added_by="Bob", purchased=True)
    purchased_created = db_instance.add_shopping_item(purchased_item)
    fetched = db_instance.get_shopping_list()
    assert any(i.id == purchased_created.id and i.purchased for i in fetched)

    db_instance.remove_shopping_item(created.id)
    db_instance.remove_shopping_item(purchased_created.id)
    assert db_instance.get_shopping_list() == []


def test_expenses_and_reimbursements(db_instance):
    expense = Expense(title="Utilities", amount=120.0, payer="Alice", involved_people=["Alice", "Bob"])
    saved_expense = db_instance.add_expense(expense)
    assert saved_expense.id is not None

    expenses = db_instance.get_expenses()
    assert len(expenses) == 1
    assert expenses[0].title == "Utilities"

    reimbursement = Reimbursement(from_person="Bob", to_person="Alice", amount=60.0, note="Bank transfer")
    saved_reimb = db_instance.add_reimbursement(reimbursement)
    assert saved_reimb.id is not None

    reimbursements = db_instance.get_reimbursements()
    assert len(reimbursements) == 1
    assert reimbursements[0].amount == 60.0


def test_clear_all_data(db_instance):
    db_instance.update_house_settings(HouseSettings(name="Demo", flatmates=["A"]))
    db_instance.add_event(
        Event(title="Temp", date=date.today(), description="", assigned_to=["A"])
    )
    db_instance.add_shopping_item(ShoppingItem(name="Bread", quantity=1, added_by="A"))
    db_instance.add_expense(
        Expense(title="Water", amount=10.0, payer="A", involved_people=["A"])
    )
    db_instance.add_reimbursement(
        Reimbursement(from_person="A", to_person="A", amount=1.0)
    )

    db_instance.clear_all_data()

    assert db_instance.get_house_settings() == HouseSettings()
    assert db_instance.get_events() == []
    assert db_instance.get_shopping_list() == []
    assert db_instance.get_expenses() == []
    assert db_instance.get_reimbursements() == []