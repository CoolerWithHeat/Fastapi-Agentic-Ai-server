
from fastapi import APIRouter, Depends
from .models import User
from .dependencies import get_current_user

router = APIRouter()

@router.get("/me")
async def read_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "purchases": [p.id for p in current_user.purchased_products],
        "messages": [m.id for m in current_user.chat_messages],
    }