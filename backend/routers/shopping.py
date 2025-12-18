from typing import List

from fastapi import APIRouter, Depends

from ..db import db
from ..models import ShoppingItem
from .auth import UserContext, get_current_user

router = APIRouter(prefix="/shopping", tags=["shopping"])

@router.get("/", response_model=List[ShoppingItem])
def get_shopping_list(current_user: UserContext = Depends(get_current_user)):
    """Retrieve all shopping items for the user's house."""
    return db.get_shopping_list(current_user.house_id)

@router.post("/", response_model=ShoppingItem)
def add_item(item: ShoppingItem, current_user: UserContext = Depends(get_current_user)):
    """Add a shopping list item.

    Args:
        item (ShoppingItem): Item details from the client.

    Returns:
        ShoppingItem: Stored item with ID.
    """
    return db.add_shopping_item(item, current_user.house_id)

@router.delete("/{item_id}")
def remove_item(item_id: int, current_user: UserContext = Depends(get_current_user)):
    """Delete a shopping item by ID.

    Args:
        item_id (int): Identifier of the item to remove.

    Returns:
        dict: Confirmation message once removed.
    """
    db.remove_shopping_item(item_id, current_user.house_id)
    return {"message": "Item removed"}