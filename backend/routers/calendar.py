from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Event
from ..db import db

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/", response_model=List[Event])
def get_events():
    """Return all scheduled events."""
    return db.get_events()

@router.post("/", response_model=Event)
def create_event(event: Event):
    """Create a new event.

    Args:
        event (Event): Event payload from the client.

    Returns:
        Event: Persisted event with ID.
    """
    return db.add_event(event)

@router.put("/{event_id}", response_model=Event)
def update_event(event_id: int, event: Event):
    """Update an existing event by its identifier.

    Args:
        event_id (int): Event ID to update.
        event (Event): New event values.

    Returns:
        Event: Updated event if found.

    Raises:
        HTTPException: If the event does not exist.
    """
    updated_event = db.update_event(event_id, event)
    if updated_event:
        return updated_event
    raise HTTPException(status_code=404, detail="Event not found")