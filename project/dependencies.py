
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .security import decode_access_token
from .models import User
from sqlalchemy.future import select

async def get_user(Authorization: str = Header(...)):
    token = Authorization.split("Bearer ")[-1].strip()
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(401, "Invalid or expired token")
    user_id = payload.get('user_id')
    return user_id