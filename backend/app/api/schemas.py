"""Request and response shapes (Pydantic). Field bounds reuse the service constants so there is one source."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.api.types import NO_NUL, SPACE, Cents, DbId, Stock, json_int
from app.services.order_rules import MAX_LINES, MAX_QUANTITY, MIN_LINES, MIN_QUANTITY

EMAIL = rf"^[^@{SPACE}\x00]+@[^@{SPACE}\x00]+\.[^@{SPACE}\x00]+$"
Role = Literal["CUSTOMER", "STAFF", "ADMIN"]
TargetStatus = Literal["PAID", "SHIPPED", "DELIVERED", "CANCELLED"]


# ---------------------------------------------------------------- users
class UserCreate(BaseModel):
    email: str = Field(pattern=EMAIL, max_length=254)
    password: str = Field(min_length=8, max_length=128, pattern=NO_NUL)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleChange(BaseModel):
    role: Role


# ---------------------------------------------------------------- catalogue
class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=100, pattern=NO_NUL)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ProductIn(BaseModel):
    sku: str = Field(min_length=1, max_length=64, pattern=rf"^[^{SPACE}\x00]+$")
    name: str = Field(min_length=1, max_length=200, pattern=NO_NUL)
    description: str = Field("", max_length=2000, pattern=NO_NUL)
    price_cents: Cents
    stock: Stock
    category_id: DbId


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    name: str
    description: str
    price_cents: int
    stock: int
    category_id: int


class ProductPage(BaseModel):
    items: list[ProductOut]
    total: int


# ---------------------------------------------------------------- orders
class OrderItemIn(BaseModel):
    """Any other field sent by the client (a price, for instance) is ignored (BR-02)."""

    product_id: DbId
    quantity: json_int(MIN_QUANTITY, MAX_QUANTITY)  # type: ignore[valid-type]


class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=MIN_LINES, max_length=MAX_LINES)


class OrderItemOut(BaseModel):
    product_id: int
    name: str
    quantity: int
    unit_price_cents: int


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    subtotal_cents: int
    discount_cents: int
    total_cents: int
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut]


class StatusChange(BaseModel):
    status: TargetStatus


# ---------------------------------------------------------------- dashboard and audit
class TopProduct(BaseModel):
    product_id: int
    name: str
    quantity: int


class LowStockProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    name: str
    stock: int


class DashboardOut(BaseModel):
    revenue_cents: int
    orders_by_status: dict[str, int]
    top_products: list[TopProduct]
    low_stock: list[LowStockProduct]
    low_stock_total: int


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    actor_id: int | None
    action: str
    entity: str
    entity_id: int | None
    details: dict[str, Any]
    created_at: datetime
