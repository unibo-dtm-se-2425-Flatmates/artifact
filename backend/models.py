from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field

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
    id: Optional[int] = None
    name: str = ""
    flatmates: List[str] = Field(default_factory=list)
    join_code: Optional[str] = None


class User(BaseModel):
    id: int
    username: str
    house_id: Optional[int] = None


class AuthResponse(BaseModel):
    token: str
    user: User
    house: HouseSettings


class RegisterRequest(BaseModel):
    username: str
    password: str
    house_name: Optional[str] = None
    house_code: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str