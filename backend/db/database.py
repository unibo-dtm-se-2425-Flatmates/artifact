import hashlib
import json
import secrets
import sqlite3
import time
from pathlib import Path
from typing import List, Optional, Tuple

from ..models import Event, Expense, HouseSettings, Reimbursement, ShoppingItem, User


class Database:
    def __init__(self):
        """Initialize the SQLite connection and ensure tables exist."""
        self.db_path = Path(__file__).resolve().parent / "flatmate.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_tables()

    # --- Setup helpers ---
    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        """Add a column to an existing table if it is missing."""
        cursor = self.conn.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if column not in columns:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            self.conn.commit()

    def _ensure_tables(self) -> None:
        """Create database tables if they do not already exist."""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS houses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                join_code TEXT UNIQUE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                house_id INTEGER,
                FOREIGN KEY (house_id) REFERENCES houses(id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                description TEXT,
                assigned_to TEXT,
                house_id INTEGER,
                FOREIGN KEY (house_id) REFERENCES houses(id)
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
                purchased INTEGER NOT NULL DEFAULT 0,
                house_id INTEGER,
                FOREIGN KEY (house_id) REFERENCES houses(id)
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
                involved_people TEXT NOT NULL,
                house_id INTEGER,
                FOREIGN KEY (house_id) REFERENCES houses(id)
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
                note TEXT,
                house_id INTEGER,
                FOREIGN KEY (house_id) REFERENCES houses(id)
            )
            """
        )

        # Backwards-compatibility: add missing house_id columns on existing DBs
        self._ensure_column("events", "house_id", "INTEGER")
        self._ensure_column("shopping_items", "house_id", "INTEGER")
        self._ensure_column("expenses", "house_id", "INTEGER")
        self._ensure_column("reimbursements", "house_id", "INTEGER")

        self.conn.commit()

    # --- Serialization helpers ---
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

    # --- Auth helpers ---
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        salt_to_use = salt or secrets.token_hex(16)
        digest = hashlib.sha256(f"{salt_to_use}{password}".encode("utf-8")).hexdigest()
        return salt_to_use, digest

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(id=row["id"], username=row["username"], house_id=row["house_id"])

    def create_house(self, name: str) -> HouseSettings:
        cursor = self.conn.execute(
            "INSERT INTO houses (name, join_code) VALUES (?, ?)",
            (name, None),
        )
        house_id = cursor.lastrowid
        join_code = str(house_id)
        self.conn.execute("UPDATE houses SET join_code = ? WHERE id = ?", (join_code, house_id))
        self.conn.commit()
        return self.get_house_settings(house_id)

    def get_house_by_code(self, code: str) -> Optional[sqlite3.Row]:
        cursor = self.conn.execute("SELECT id, name, join_code FROM houses WHERE join_code = ?", (code,))
        return cursor.fetchone()

    def get_house_settings(self, house_id: int) -> HouseSettings:
        cursor = self.conn.execute("SELECT id, name, join_code FROM houses WHERE id = ?", (house_id,))
        row = cursor.fetchone()
        if not row:
            return HouseSettings()
        members = self.get_house_members(house_id)
        return HouseSettings(id=row["id"], name=row["name"] or "", flatmates=members, join_code=row["join_code"])

    def update_house_settings(self, house_id: int, settings: HouseSettings) -> HouseSettings:
        self.conn.execute("UPDATE houses SET name = ? WHERE id = ?", (settings.name, house_id))
        self.conn.commit()
        return self.get_house_settings(house_id)

    def get_house_members(self, house_id: int) -> List[str]:
        cursor = self.conn.execute("SELECT username FROM users WHERE house_id = ? ORDER BY username ASC", (house_id,))
        return [row["username"] for row in cursor.fetchall()]

    def create_user(self, username: str, password: str, house_id: int) -> User:
        salt, hashed = self._hash_password(password)
        cursor = self.conn.execute(
            "INSERT INTO users (username, password_hash, password_salt, house_id) VALUES (?, ?, ?, ?)",
            (username, hashed, salt, house_id),
        )
        self.conn.commit()
        return self._row_to_user(self.conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone())

    def get_user_by_username(self, username: str) -> Optional[User]:
        cursor = self.conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return self._row_to_user(row) if row else None

    def verify_user_credentials(self, username: str, password: str) -> Optional[User]:
        cursor = self.conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return None
        salt = row["password_salt"]
        _, hashed = self._hash_password(password, salt)
        if hashed != row["password_hash"]:
            return None
        return self._row_to_user(row)

    def create_session_token(self, user_id: int) -> str:
        token = secrets.token_hex(16)
        self.conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, user_id, time.time()),
        )
        self.conn.commit()
        return token

    def get_user_by_token(self, token: str) -> Optional[User]:
        cursor = self.conn.execute(
            """
            SELECT users.id, users.username, users.house_id
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (token,),
        )
        row = cursor.fetchone()
        return self._row_to_user(row) if row else None

    # --- Domain data accessors ---
    def add_event(self, event: Event, house_id: int) -> Event:
        cursor = self.conn.execute(
            """
            INSERT INTO events (title, date, start_time, end_time, description, assigned_to, house_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.title,
                event.date.isoformat(),
                event.start_time.isoformat() if event.start_time else None,
                event.end_time.isoformat() if event.end_time else None,
                event.description,
                self._serialize_list(event.assigned_to),
                house_id,
            ),
        )
        self.conn.commit()
        return event.model_copy(update={"id": cursor.lastrowid})

    def update_event(self, event_id: int, event: Event, house_id: int) -> Optional[Event]:
        cursor = self.conn.execute("SELECT id FROM events WHERE id = ? AND house_id = ?", (event_id, house_id))
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
            WHERE id = ? AND house_id = ?
            """,
            (
                event.title,
                event.date.isoformat(),
                event.start_time.isoformat() if event.start_time else None,
                event.end_time.isoformat() if event.end_time else None,
                event.description,
                self._serialize_list(event.assigned_to),
                event_id,
                house_id,
            ),
        )
        self.conn.commit()
        return event.model_copy(update={"id": event_id})

    def get_events(self, house_id: int) -> List[Event]:
        cursor = self.conn.execute(
            """
            SELECT id, title, date, start_time, end_time, description, assigned_to
            FROM events
            WHERE house_id = ?
            ORDER BY date ASC, (start_time IS NULL), start_time ASC, id ASC
            """,
            (house_id,),
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

    def add_shopping_item(self, item: ShoppingItem, house_id: int) -> ShoppingItem:
        cursor = self.conn.execute(
            """
            INSERT INTO shopping_items (name, quantity, added_by, purchased, house_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (item.name, item.quantity, item.added_by, 1 if item.purchased else 0, house_id),
        )
        self.conn.commit()
        return item.model_copy(update={"id": cursor.lastrowid})

    def get_shopping_list(self, house_id: int) -> List[ShoppingItem]:
        cursor = self.conn.execute(
            """
            SELECT id, name, quantity, added_by, purchased
            FROM shopping_items
            WHERE house_id = ?
            ORDER BY id ASC
            """,
            (house_id,),
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

    def remove_shopping_item(self, item_id: int, house_id: int) -> None:
        self.conn.execute("DELETE FROM shopping_items WHERE id = ? AND house_id = ?", (item_id, house_id))
        self.conn.commit()

    def add_expense(self, expense: Expense, house_id: int) -> Expense:
        cursor = self.conn.execute(
            """
            INSERT INTO expenses (title, amount, payer, involved_people, house_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                expense.title,
                expense.amount,
                expense.payer,
                self._serialize_list(expense.involved_people),
                house_id,
            ),
        )
        self.conn.commit()
        return expense.model_copy(update={"id": cursor.lastrowid})

    def get_expenses(self, house_id: int) -> List[Expense]:
        cursor = self.conn.execute(
            """
            SELECT id, title, amount, payer, involved_people
            FROM expenses
            WHERE house_id = ?
            ORDER BY id ASC
            """,
            (house_id,),
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

    def add_reimbursement(self, reimbursement: Reimbursement, house_id: int) -> Reimbursement:
        cursor = self.conn.execute(
            """
            INSERT INTO reimbursements (from_person, to_person, amount, note, house_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                reimbursement.from_person,
                reimbursement.to_person,
                reimbursement.amount,
                reimbursement.note,
                house_id,
            ),
        )
        self.conn.commit()
        return reimbursement.model_copy(update={"id": cursor.lastrowid})

    def get_reimbursements(self, house_id: int) -> List[Reimbursement]:
        cursor = self.conn.execute(
            """
            SELECT id, from_person, to_person, amount, note
            FROM reimbursements
            WHERE house_id = ?
            ORDER BY id ASC
            """,
            (house_id,),
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

    def clear_house_data(self, house_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM events WHERE house_id = ?", (house_id,))
        cursor.execute("DELETE FROM shopping_items WHERE house_id = ?", (house_id,))
        cursor.execute("DELETE FROM expenses WHERE house_id = ?", (house_id,))
        cursor.execute("DELETE FROM reimbursements WHERE house_id = ?", (house_id,))
        self.conn.commit()

    def delete_house(self, house_id: int) -> None:
        """Remove a house and all its related data, users, and sessions."""
        cursor = self.conn.cursor()
        # Clear domain data first
        cursor.execute("DELETE FROM events WHERE house_id = ?", (house_id,))
        cursor.execute("DELETE FROM shopping_items WHERE house_id = ?", (house_id,))
        cursor.execute("DELETE FROM expenses WHERE house_id = ?", (house_id,))
        cursor.execute("DELETE FROM reimbursements WHERE house_id = ?", (house_id,))
        # Remove sessions for users in this house
        cursor.execute(
            "DELETE FROM sessions WHERE user_id IN (SELECT id FROM users WHERE house_id = ?)",
            (house_id,),
        )
        # Remove users and house
        cursor.execute("DELETE FROM users WHERE house_id = ?", (house_id,))
        cursor.execute("DELETE FROM houses WHERE id = ?", (house_id,))
        self.conn.commit()


db = Database()