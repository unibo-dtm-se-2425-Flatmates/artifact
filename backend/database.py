from typing import List, Dict
from .models import Event, ShoppingItem, Expense

class Database:
    def __init__(self):
        self.events: Dict[int, Event] = {}
        self.shopping_list: Dict[int, ShoppingItem] = {}
        self.expenses: Dict[int, Expense] = {}
        
        self._event_id_counter = 1
        self._item_id_counter = 1
        self._expense_id_counter = 1

    def add_event(self, event: Event) -> Event:
        event.id = self._event_id_counter
        self.events[self._event_id_counter] = event
        self._event_id_counter += 1
        return event

    def get_events(self) -> List[Event]:
        return list(self.events.values())

    def add_shopping_item(self, item: ShoppingItem) -> ShoppingItem:
        item.id = self._item_id_counter
        self.shopping_list[self._item_id_counter] = item
        self._item_id_counter += 1
        return item

    def get_shopping_list(self) -> List[ShoppingItem]:
        return list(self.shopping_list.values())

    def remove_shopping_item(self, item_id: int):
        if item_id in self.shopping_list:
            del self.shopping_list[item_id]

    def add_expense(self, expense: Expense) -> Expense:
        expense.id = self._expense_id_counter
        self.expenses[self._expense_id_counter] = expense
        self._expense_id_counter += 1
        return expense

    def get_expenses(self) -> List[Expense]:
        return list(self.expenses.values())

db = Database()