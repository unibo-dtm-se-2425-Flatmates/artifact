from fastapi import APIRouter
from typing import List
from ..models import ShoppingItem
from ..database import db

router = APIRouter(prefix="/shopping", tags=["shopping"])

@router.get("/", response_model=List[ShoppingItem])
def get_shopping_list():
    return db.get_shopping_list()

@router.post("/", response_model=ShoppingItem)
def add_item(item: ShoppingItem):
    return db.add_shopping_item(item)

@router.delete("/{item_id}")
def remove_item(item_id: int):
    db.remove_shopping_item(item_id)
    return {"message": "Item removed"}