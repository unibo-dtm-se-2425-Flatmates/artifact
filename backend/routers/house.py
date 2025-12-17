from fastapi import APIRouter
from ..models import HouseSettings
from ..db import db

router = APIRouter(prefix="/house", tags=["house"])

@router.get("/", response_model=HouseSettings)
def get_house_settings():
    return db.get_house_settings()

@router.post("/", response_model=HouseSettings)
def update_house_settings(settings: HouseSettings):
    return db.update_house_settings(settings)