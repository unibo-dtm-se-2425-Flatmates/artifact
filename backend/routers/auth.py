from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional

from ..db import db
from ..models import AuthResponse, LoginRequest, RegisterRequest, User

router = APIRouter(prefix="/auth", tags=["auth"])


class UserContext(User):
    """Lightweight context returned by the auth dependency."""


def get_current_user(authorization: Optional[str] = Header(None)) -> UserContext:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    user = db.get_user_by_token(token)
    if not user or user.house_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return UserContext(**user.model_dump())


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest):
    if db.get_user_by_username(request.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    house_id: Optional[int] = None
    if request.house_code:
        house = db.get_house_by_code(request.house_code)
        if not house:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="House not found")
        house_id = house["id"]
    else:
        new_house = db.create_house(request.house_name or f"{request.username}'s House")
        house_id = new_house.id

    user = db.create_user(request.username, request.password, house_id)
    token = db.create_session_token(user.id)
    house_settings = db.get_house_settings(house_id)
    return AuthResponse(token=token, user=user, house=house_settings)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):
    user = db.verify_user_credentials(request.username, request.password)
    if not user or user.house_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = db.create_session_token(user.id)
    house_settings = db.get_house_settings(user.house_id)
    return AuthResponse(token=token, user=user, house=house_settings)


@router.get("/me", response_model=AuthResponse)
def me(current_user: UserContext = Depends(get_current_user)):
    house_settings = db.get_house_settings(current_user.house_id)
    return AuthResponse(token="", user=current_user, house=house_settings)