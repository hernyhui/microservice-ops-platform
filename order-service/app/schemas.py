from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OrderCreate(BaseModel):
    product_id: str
    product_name: str
    quantity: int = Field(gt=0, description="购买数量，必须大于0")
    unit_price: int = Field(gt=0, default=100, description="单价（分）")


class OrderResponse(BaseModel):
    id: int
    order_no: str
    product_id: str
    product_name: str
    quantity: int
    total_amount: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
