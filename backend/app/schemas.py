from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserCreate(BaseModel):
    email: str = Field(pattern=EMAIL, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    name: str
    description: str
    price_cents: int
    stock: int


class ProductPage(BaseModel):
    items: list[ProductOut]
    total: int


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=99)


class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1, max_length=50)


class OrderItemOut(BaseModel):
    product_id: int
    name: str
    quantity: int
    unit_price_cents: int


class OrderOut(BaseModel):
    id: int
    status: str
    total_cents: int
    created_at: datetime
    items: list[OrderItemOut]
