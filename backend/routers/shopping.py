from fastapi import APIRouter
from typing import List
from ..models import ShoppingItem
from ..db import db

router = APIRouter(prefix="/shopping", tags=["shopping"])

@router.get("/", response_model=List[ShoppingItem])
def get_shopping_list():
    """Retrieve all shopping items."""
    return db.get_shopping_list()

@router.post("/", response_model=ShoppingItem)
def add_item(item: ShoppingItem):
    """Add a shopping list item.

    Args:
        item (ShoppingItem): Item details from the client.

    Returns:
        ShoppingItem: Stored item with ID.
    """
    return db.add_shopping_item(item)

@router.delete("/{item_id}")
def remove_item(item_id: int):
    """Delete a shopping item by ID.

    Args:
        item_id (int): Identifier of the item to remove.

    Returns:
        dict: Confirmation message once removed.
    """
    db.remove_shopping_item(item_id)
    return {"message": "Item removed"}