from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time

class Event(BaseModel):
    id: Optional[int] = None
    title: str
    date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    assigned_to: List[str] = Field(default_factory=list)

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
    involved_people: List[str] = Field(default_factory=list)  # Names of people splitting this expense

class Debt(BaseModel):
    debtor: str
    creditor: str
    amount: float


class Reimbursement(BaseModel):
    id: Optional[int] = None
    from_person: str
    to_person: str
    amount: float
    note: Optional[str] = None

class HouseSettings(BaseModel):
    name: str = ""
    flatmates: List[str] = Field(default_factory=list)