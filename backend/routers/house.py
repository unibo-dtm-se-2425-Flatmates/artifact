from fastapi import APIRouter
from ..models import HouseSettings
from ..db import db

router = APIRouter(prefix="/house", tags=["house"])

@router.get("/", response_model=HouseSettings)
def get_house_settings():
    """Return the saved house configuration."""
    return db.get_house_settings()

@router.post("/", response_model=HouseSettings)
def update_house_settings(settings: HouseSettings):
    """Create or update the house configuration.

    Args:
        settings (HouseSettings): House name and flatmates.

    Returns:
        HouseSettings: Persisted configuration.
    """
    return db.update_house_settings(settings)


@router.delete("/reset")
def reset_house_data():
    """Delete house settings and all related data."""
    db.clear_all_data()
    return {"message": "House and data reset"}