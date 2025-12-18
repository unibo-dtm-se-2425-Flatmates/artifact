from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..db import db
from ..models import Event
from .auth import UserContext, get_current_user

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/", response_model=List[Event])
def get_events(current_user: UserContext = Depends(get_current_user)):
    """Return all scheduled events for the authenticated user's house."""
    return db.get_events(current_user.house_id)

@router.post("/", response_model=Event)
def create_event(event: Event, current_user: UserContext = Depends(get_current_user)):
    """Create a new event.

    Args:
        event (Event): Event payload from the client.

    Returns:
        Event: Persisted event with ID.
    """
    return db.add_event(event, current_user.house_id)

@router.put("/{event_id}", response_model=Event)
def update_event(event_id: int, event: Event, current_user: UserContext = Depends(get_current_user)):
    """Update an existing event by its identifier.

    Args:
        event_id (int): Event ID to update.
        event (Event): New event values.

    Returns:
        Event: Updated event if found.

    Raises:
        HTTPException: If the event does not exist.
    """
    updated_event = db.update_event(event_id, event, current_user.house_id)
    if updated_event:
        return updated_event
    raise HTTPException(status_code=404, detail="Event not found")