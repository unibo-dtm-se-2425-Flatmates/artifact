from typing import List, Dict, Optional
from .models import Event, ShoppingItem, Expense, HouseSettings

class Database:
    def __init__(self):
        self.events: Dict[int, Event] = {}
        self.shopping_list: Dict[int, ShoppingItem] = {}
        self.expenses: Dict[int, Expense] = {}
        self.house_settings = HouseSettings()
        
        self._event_id_counter = 1
        self._item_id_counter = 1
        self._expense_id_counter = 1

    def get_house_settings(self) -> HouseSettings:
        return self.house_settings

    def update_house_settings(self, settings: HouseSettings) -> HouseSettings:
        self.house_settings = settings
        return self.house_settings

    def add_event(self, event: Event) -> Event:
        event.id = self._event_id_counter
        self.events[self._event_id_counter] = event
        self._event_id_counter += 1
        return event

    def update_event(self, event_id: int, event: Event) -> Optional[Event]:
        if event_id in self.events:
            event.id = event_id
            self.events[event_id] = event
            return event
        return None

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