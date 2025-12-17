from fastapi import APIRouter
from typing import List
from ..models import Event
from ..database import db

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/", response_model=List[Event])
def get_events():
    return db.get_events()

@router.post("/", response_model=Event)
def create_event(event: Event):
    return db.add_event(event)