from fastapi import FastAPI, Depends, HTTPException, Header, Request
from sqlalchemy.orm import selectinload
from .models import User, Product, Purchase, ChatMessage
from .database import AsyncSessionLocal
from .schemas import (
    userSerializer, 
    productSerializer, 
    purchaseSerializer, 
    chatMessageStruct
)
from pydantic import BaseModel, Field
from collections import defaultdict
from .auth_mng import router
from .dependencies import get_user
from typing import Optional
from .graph import graph_builder, integrity, nodes
from langchain.messages import HumanMessage
from langchain_core.messages.base import messages_to_dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from openai import AuthenticationError

app = FastAPI()

app.include_router(router)

rate_limit_store = defaultdict(list)
ip_rate_limit_store = defaultdict(lambda: None)

class UserDataStr(BaseModel):
    username: str = Field(max_length=25, min_length=2)
    password: str = Field(min_length=12, max_length=50)

class productDataStruct(BaseModel):
    name: str = Field(max_length=50, min_length=2)
    price: float

class purchaseStatusStruct(BaseModel):
    status_index:  int

class SupportMessage(BaseModel):
    message: str = Field(..., min_length=1)

class ProductSaveStruct(BaseModel):
    products: list[int]


def rate_limit_ip(request: Request, seconds: int = 2):
    """
    Raises HTTP 429 if the last request from the same IP was less than `seconds` ago.
    """
    # Get client IP from request
    client_ip = request.client.host
    now = datetime.now()
    last_request = ip_rate_limit_store.get(client_ip)

    if last_request and (now - last_request).total_seconds() < seconds:
        raise HTTPException(
            status_code=429, 
            detail=f"Too many requests. Wait {seconds} seconds."
        )

    # Update last request timestamp
    ip_rate_limit_store[client_ip] = now

def rate_limit_user(user_id: int, seconds: int = 2):
    now = datetime.now()
    last_request = rate_limit_store.get(user_id)
    
    if last_request and (now - last_request).total_seconds() < seconds:
        raise HTTPException(status_code=429, detail=f"Wait {seconds} seconds between requests")

    rate_limit_store[user_id] = now

    
async def query_user(db: AsyncSession, user_id: int, till: str = 'all') -> User | None:
    """
    Query a user and optionally load relationships.

    Returns:
    User instance or None if not found
    """
    stmt = select(User).where(User.id == user_id)


    if till == 'all':
        stmt = stmt.options(
            selectinload(User.purchased_products).selectinload(Purchase.purchased_products),
            selectinload(User.chat_messages)
        )
    elif till == 'chat_messages':
        stmt = stmt.options(selectinload(User.chat_messages))
    elif till == 'purchased_products':
        stmt = stmt.options(selectinload(User.purchased_products).selectinload(Purchase.purchased_products))

    result = await db.execute(stmt)
    user = result.scalars().first()
    if result: return user
    else: raise HTTPException(status_code=404, detail='User was not found!')

def getContext(user: User | None = None) -> list[dict]:
    if user:
        try:
            messages = [
                chatMessageStruct.model_validate(msg, from_attributes=True).model_dump()
                for msg in getattr(user, "chat_messages", [])
            ]
            return integrity.enforce_sequence(messages)
        except Exception as error:
            print("[getContext error]:", error)
    return []

async def handleSupportMessage(user_message: dict, prev: list[dict] | None = None):
    LLM = graph_builder.graph
    prev_messages = prev or []
    context = prev_messages + user_message
    try:
        response = await LLM.ainvoke({'messages': context})
        response_msg = response.get('messages')
        return response_msg or []
    except AttributeError: 
        nodes.outputKeyError()
        return None
    except AuthenticationError:
        nodes.outputKeyError(True)
    except Exception as error:
        print(error)
        return None
    
async def async_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.post('/create_user', response_model=userSerializer)
async def produce_user(user_data: UserDataStr, request: Request, db: AsyncSession = Depends(async_db)):
    rate_limit_ip(request, 1)
    data = user_data.dict()
    new_user = User(**data)
    valid_username = await new_user.valid_username(db, data.get('username'))
    if valid_username:
        db.add(new_user)
        await db.commit()
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.purchased_products).selectinload(Purchase.purchased_products),
                selectinload(User.chat_messages),
            )
            .where(User.id == new_user.id)
        )
        user = result.scalars().first()
        return user
    else:  raise HTTPException(status_code=409, detail='User with such a username already exists!')
    

@app.get('/myprofile')
async def give_profile(user_id: int = Depends(get_user), db: AsyncSession = Depends(async_db)):
    user = await db.execute(select(User).where(User.id==user_id))
    result = user.scalars().first()
    return {'id': result.id, 'username': result.username}


@app.post('/create_product', response_model=productSerializer)
async def create_product(details: productDataStruct, db: AsyncSession = Depends(async_db)):
    product_details = details.dict()
    try:
        product = Product(**product_details)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product
    except Exception as error: 
        print(error)
        raise HTTPException(status_code=500, detail='Something went wrong')

@app.post('/register_purchase', response_model=userSerializer)
async def save_purchases(
        products: ProductSaveStruct, 
        request: Request,
        user_id: User = Depends(get_user), 
        db: AsyncSession = Depends(async_db),
    ):
    rate_limit_ip(request, 1)
    user = await query_user(db, user_id)
    ids = products.dict().get('products')
    req_products = await db.execute(select(Product).where(Product.id.in_(ids)))
    products = req_products.scalars().all()
    if products and user:
        new_purchase = Purchase()
        new_purchase.purchased_products = products
        new_purchase.owner_id = user.id
        db.add(new_purchase)
        try:
            await db.commit()
        except Exception as error: 
            await db.rollback()
            print(error)
        user_query = await db.execute(select(User)
                        .where(User.id == user.id)
                        .options(selectinload(User.purchased_products).selectinload(Purchase.purchased_products))   
                    )
        updated_user = user_query.scalar()
        return updated_user
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized request')
    if not (len(ids) == len(products)): 
        raise HTTPException(status_code=401, detail='Some/all products requested not found!')
    
@app.get('/user_purchases', response_model=Optional[list[purchaseSerializer]])
async def give_pruchases(user_id: int = Depends(get_user), db: AsyncSession = Depends(async_db)):
    user = await query_user(db, user_id, 'purchased_products')
    return user.purchased_products


@app.get('/purchase/{purchase_id}', response_model=Optional[purchaseSerializer])
async def give_purchase_batches(purchase_id: int, db: AsyncSession = Depends(async_db)):
    result = await db.execute(select(Purchase).where(Purchase.id == purchase_id).options(selectinload(Purchase.purchased_products)))
    purchase = result.scalars().first()
    if purchase: return purchase
    raise HTTPException(status_code=404, detail='Resource not found')

@app.post('/update_order_status/{order_id}')
async def update_status(order_id: int, status_index: purchaseStatusStruct, db: AsyncSession = Depends(async_db)):
    status_index = status_index.dict()
    status_index = status_index.get('status_index') if status_index else 1
    result = await db.execute(select(Purchase).where(Purchase.id == order_id))
    req_purchase = result.scalars().first()
    if not req_purchase:
        raise HTTPException(status_code=404, detail="Product not found!")
    req_purchase.fulfillment_stage = status_index
    await db.commit()
    await db.refresh(req_purchase)
    return req_purchase


@app.get('/products', response_model=list[productSerializer])
async def give_products(db: AsyncSession = Depends(async_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products

async def updateMessages(user: User, new_messages: list[dict], db: AsyncSession) -> User:
    for each_new in new_messages:
        msg = ChatMessage(message=each_new, belongs_to=user.id)
        db.add(msg)
    try:
        await db.commit()
    except Exception as error:
        await db.rollback()
        print("[updateMessages Error]:", error)
    return user
    

@app.post('/support')
async def handle_inquiry(inquiry: SupportMessage, request: Request, user_id: int=Depends(get_user), db: AsyncSession = Depends(async_db)):
    # rate_limit_ip(request, 1) # Enable this in production, rate limits by IP !
    user = await query_user(db, user_id, 'chat_messages')
    rate_limit_user(user.id, seconds=2)
    message = inquiry.dict().get('message', '')
    text_answer = 'Sorry assistant is not available currently.'
    composed_message = messages_to_dict([HumanMessage(content=message)])
    context = getContext(user)
    response = await handleSupportMessage(composed_message, context) or {} # for memorized response takes 1.3 - 1.5 second, for inquiry with tool call 2.85-3.0 secs
    if response:
        new_messages = response[len(context):]
        await updateMessages(user, new_messages, db)
        text_answer = new_messages[-1].get('data', {}).get('content') or text_answer
    return {'answer': text_answer}