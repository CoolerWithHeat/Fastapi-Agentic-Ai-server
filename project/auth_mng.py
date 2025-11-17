from passlib.context import CryptContext
from pydantic import Field, BaseModel
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from .security import create_access_token
from sqlalchemy.future import select
from .database import AsyncSessionLocal


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_hashed(password):
    hash_clues = ["$2b$", "$2a$", "$2c$"] 
    till_start = password[:3]
    return (till_start in hash_clues) and (len(password) == 60)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str = Field(max_length=50), hashed_password: str = Field(max_length=60, min_length=60)) -> bool:
    result = False 
    try: result = pwd_context.verify(plain_password, hashed_password)
    except: pass
    return result

def generate_token() -> str:
    prefix = "~18sH"
    length = 60
    remaining_length = length - len(prefix)
    charset = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(charset) for _ in range(remaining_length))
    return prefix + random_part

router = APIRouter()

async def async_db():
    async with AsyncSessionLocal() as session:
        yield session

class UserDataStr(BaseModel):
    username: str = Field(max_length=25, min_length=2)
    password: str = Field(min_length=12, max_length=50)

@router.post("/login")
async def login_endpoint(user_data: UserDataStr, db: AsyncSession = Depends(async_db)):
    result = await db.execute(
        select(models.User).where(models.User.username == user_data.username)
    )
    user = result.scalars().first()
    if not user or not user.check_password(user_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_data = {"user_id": user.id}
    jwt_token = create_access_token(token_data)
    
    return {"access_token": jwt_token, "token_type": "bearer"}