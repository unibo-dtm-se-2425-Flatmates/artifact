from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Event(BaseModel):
    id: Optional[int] = None
    title: str
    date: date
    description: Optional[str] = None

class ShoppingItem(BaseModel):
    id: Optional[int] = None
    name: str
    quantity: int = 1
    added_by: str
    purchased: bool = False

class Expense(BaseModel):
    id: Optional[int] = None
    title: str
    amount: float
    payer: str
    involved_people: List[str]  # List of names of people splitting this expense

class Debt(BaseModel):
    debtor: str
    creditor: str
    amount: float