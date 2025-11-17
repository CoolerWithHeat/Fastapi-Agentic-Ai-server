from pydantic import BaseModel, Field
from typing import Optional

class tokenSerializer(BaseModel):
    token: str

class productSerializer(BaseModel):
    id: int
    name: str
    price: float

class purchaseSerializer(BaseModel):
    id: int
    purchased_products: Optional[list[productSerializer]] = Field(default_factory=list)
    fulfillment_stage: str | None=None
    
    class Config:
        from_attributes = True

class chatMessageStruct(BaseModel):
    message: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}

    def model_dump(self, *args, **kwargs):
        return self.message

class userSerializer(BaseModel):
    id: int
    username: str
    purchased_products: list[purchaseSerializer]
    chat_messages: list[chatMessageStruct] = Field(default_factory=list)
    class Config:
        from_attributes = True