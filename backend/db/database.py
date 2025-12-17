import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from ..models import Event, ShoppingItem, Expense, HouseSettings, Reimbursement


class Database:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parent / "flatmate.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                description TEXT,
                assigned_to TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS shopping_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                added_by TEXT NOT NULL,
                purchased INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                payer TEXT NOT NULL,
                involved_people TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reimbursements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_person TEXT NOT NULL,
                to_person TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS house_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT,
                flatmates TEXT
            )
            """
        )
        self.conn.commit()

    @staticmethod
    def _serialize_list(values: Optional[List[str]]) -> str:
        return json.dumps(values or [])

    @staticmethod
    def _deserialize_list(raw: Optional[str]) -> List[str]:
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    def get_house_settings(self) -> HouseSettings:
        cursor = self.conn.execute("SELECT name, flatmates FROM house_settings WHERE id = 1")
        row = cursor.fetchone()
        if not row:
            return HouseSettings()
        return HouseSettings(
            name=row["name"] or "",
            flatmates=self._deserialize_list(row["flatmates"]),
        )

    def update_house_settings(self, settings: HouseSettings) -> HouseSettings:
        flatmates_serialized = self._serialize_list(settings.flatmates)
        self.conn.execute(
            """
            INSERT INTO house_settings (id, name, flatmates)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                flatmates = excluded.flatmates
            """,
            (settings.name, flatmates_serialized),
        )
        self.conn.commit()
        return settings

    def add_event(self, event: Event) -> Event:
        cursor = self.conn.execute(
            """
            INSERT INTO events (title, date, start_time, end_time, description, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event.title,
                event.date.isoformat(),
                event.start_time.isoformat() if event.start_time else None,
                event.end_time.isoformat() if event.end_time else None,
                event.description,
                self._serialize_list(event.assigned_to),
            ),
        )
        self.conn.commit()
        return event.copy(update={"id": cursor.lastrowid})

    def update_event(self, event_id: int, event: Event) -> Optional[Event]:
        cursor = self.conn.execute("SELECT id FROM events WHERE id = ?", (event_id,))
        if not cursor.fetchone():
            return None
        self.conn.execute(
            """
            UPDATE events
            SET title = ?,
                date = ?,
                start_time = ?,
                end_time = ?,
                description = ?,
                assigned_to = ?
            WHERE id = ?
            """,
            (
                event.title,
                event.date.isoformat(),
                event.start_time.isoformat() if event.start_time else None,
                event.end_time.isoformat() if event.end_time else None,
                event.description,
                self._serialize_list(event.assigned_to),
                event_id,
            ),
        )
        self.conn.commit()
        return event.copy(update={"id": event_id})

    def get_events(self) -> List[Event]:
        cursor = self.conn.execute(
            """
            SELECT id, title, date, start_time, end_time, description, assigned_to
            FROM events
            ORDER BY date ASC, (start_time IS NULL), start_time ASC, id ASC
            """
        )
        events: List[Event] = []
        for row in cursor.fetchall():
            events.append(
                Event(
                    id=row["id"],
                    title=row["title"],
                    date=row["date"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    description=row["description"],
                    assigned_to=self._deserialize_list(row["assigned_to"]),
                )
            )
        return events

    def add_shopping_item(self, item: ShoppingItem) -> ShoppingItem:
        cursor = self.conn.execute(
            """
            INSERT INTO shopping_items (name, quantity, added_by, purchased)
            VALUES (?, ?, ?, ?)
            """,
            (item.name, item.quantity, item.added_by, 1 if item.purchased else 0),
        )
        self.conn.commit()
        return item.copy(update={"id": cursor.lastrowid})

    def get_shopping_list(self) -> List[ShoppingItem]:
        cursor = self.conn.execute(
            """
            SELECT id, name, quantity, added_by, purchased
            FROM shopping_items
            ORDER BY id ASC
            """
        )
        items: List[ShoppingItem] = []
        for row in cursor.fetchall():
            items.append(
                ShoppingItem(
                    id=row["id"],
                    name=row["name"],
                    quantity=row["quantity"],
                    added_by=row["added_by"],
                    purchased=bool(row["purchased"]),
                )
            )
        return items

    def remove_shopping_item(self, item_id: int) -> None:
        self.conn.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))
        self.conn.commit()

    def add_expense(self, expense: Expense) -> Expense:
        cursor = self.conn.execute(
            """
            INSERT INTO expenses (title, amount, payer, involved_people)
            VALUES (?, ?, ?, ?)
            """,
            (
                expense.title,
                expense.amount,
                expense.payer,
                self._serialize_list(expense.involved_people),
            ),
        )
        self.conn.commit()
        return expense.copy(update={"id": cursor.lastrowid})

    def get_expenses(self) -> List[Expense]:
        cursor = self.conn.execute(
            """
            SELECT id, title, amount, payer, involved_people
            FROM expenses
            ORDER BY id ASC
            """
        )
        expenses: List[Expense] = []
        for row in cursor.fetchall():
            expenses.append(
                Expense(
                    id=row["id"],
                    title=row["title"],
                    amount=row["amount"],
                    payer=row["payer"],
                    involved_people=self._deserialize_list(row["involved_people"]),
                )
            )
        return expenses

    def add_reimbursement(self, reimbursement: Reimbursement) -> Reimbursement:
        cursor = self.conn.execute(
            """
            INSERT INTO reimbursements (from_person, to_person, amount, note)
            VALUES (?, ?, ?, ?)
            """,
            (
                reimbursement.from_person,
                reimbursement.to_person,
                reimbursement.amount,
                reimbursement.note,
            ),
        )
        self.conn.commit()
        return reimbursement.copy(update={"id": cursor.lastrowid})

    def get_reimbursements(self) -> List[Reimbursement]:
        cursor = self.conn.execute(
            """
            SELECT id, from_person, to_person, amount, note
            FROM reimbursements
            ORDER BY id ASC
            """
        )
        reimbursements: List[Reimbursement] = []
        for row in cursor.fetchall():
            reimbursements.append(
                Reimbursement(
                    id=row["id"],
                    from_person=row["from_person"],
                    to_person=row["to_person"],
                    amount=row["amount"],
                    note=row["note"],
                )
            )
        return reimbursements


db = Database()