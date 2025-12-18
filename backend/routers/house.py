from fastapi import APIRouter, Depends

from ..db import db
from ..models import HouseSettings
from .auth import UserContext, get_current_user

router = APIRouter(prefix="/house", tags=["house"])

@router.get("/", response_model=HouseSettings)
def get_house_settings(current_user: UserContext = Depends(get_current_user)):
    """Return the saved house configuration for the current user."""
    return db.get_house_settings(current_user.house_id)

@router.post("/", response_model=HouseSettings)
def update_house_settings(settings: HouseSettings, current_user: UserContext = Depends(get_current_user)):
    """Update the current house configuration (name only)."""
    settings.flatmates = db.get_house_members(current_user.house_id)
    return db.update_house_settings(current_user.house_id, settings)


@router.delete("/reset")
def reset_house_data(current_user: UserContext = Depends(get_current_user)):
    """Delete all data for the current house (events, shopping, expenses, reimbursements)."""
    db.clear_house_data(current_user.house_id)
    return {"message": "House and data reset"}


@router.delete("/delete")
def delete_house(current_user: UserContext = Depends(get_current_user)):
    """Delete the current house, its users, sessions, and all related data."""
    db.delete_house(current_user.house_id)
    return {"message": "House deleted"}