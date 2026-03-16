# app/routes/users.py
from fastapi import APIRouter
from app.services.users import get_user

router = APIRouter()

@router.get("/{steamid}")
def read_user(steamid: str):
    user = get_user(steamid)
    if not user:
        return {"error": "User not found"}
    return {"user": user}