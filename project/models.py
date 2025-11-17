from sqlalchemy import Column, String, Integer, ForeignKey, Float, Table, JSON, Date, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.future import select
from .database import Base
from .auth_mng import hash_password, verify_password, is_hashed
from datetime import datetime, timezone

PurchasePattern = Table(
    "purchase_association",
    Base.metadata,
    Column("purchase_id", ForeignKey("purchases.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)

order_stage = {
    1: 'processing',
    2: 'on the way',
    3: 'delivered',
}

class User(Base):

    __tablename__ = 'users'
     
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25), unique=True)
    password = Column(String(60))
    purchased_products = relationship('Purchase', back_populates='belongs_to', cascade='all, delete')
    chat_messages = relationship('ChatMessage', back_populates='of_user', cascade='all, delete', order_by='ChatMessage.id')

    async def valid_username(self, db, incoming_username):
        is_unique = False
        try:
            if db:    
                user = await db.execute(
                    select(User).where(User.username == incoming_username)
                )
                user_found = user.scalars().first()
                if not user_found:
                    is_unique = True
        except:
            print('[log]: Username uniqueness verification failed!')
        return is_unique
    
    def check_password(self, password):
        saved_password = self.password
        entered_password = password
        return verify_password(entered_password, saved_password)
    
    @validates('password')
    def validate_password(self, field_name, field_value):
        already_hashed = is_hashed(field_value)
        if not already_hashed:
            return hash_password(field_value)
        return field_value

class Purchase(Base):

    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    fulfillment_stage = Column(String(50), default=order_stage[1])
    belongs_to = relationship('User', back_populates='purchased_products')
    purchased_products = relationship(
        'Product', 
        secondary=PurchasePattern, 
        back_populates="purchase_batch"
    )

    @validates('fulfillment_stage')
    def order_status(self, field_name, field_value):
        field_value = field_value
        try: 
            field_value = int(field_value)
        except Exception as error: 
            field_name = 1
            print(error)
        stage_index = min(field_value, len(order_stage.keys()))
        return order_stage[stage_index]
    

class Product(Base):

    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    price = Column(Float)
    purchase_batch = relationship(
        'Purchase', secondary=PurchasePattern, back_populates="purchased_products"
    )

class ChatMessage(Base):
    
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    message = Column(JSON, nullable=True)
    belongs_to = Column(Integer, ForeignKey('users.id'))
    of_user = relationship('User', back_populates='chat_messages')
    timestamp = Column(Date, default=datetime.now())