from fastapi import APIRouter, HTTPException
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

@router.put("/{event_id}", response_model=Event)
def update_event(event_id: int, event: Event):
    updated_event = db.update_event(event_id, event)
    if updated_event:
        return updated_event
    raise HTTPException(status_code=404, detail="Event not found")