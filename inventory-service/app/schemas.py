from pydantic import BaseModel, Field
from datetime import datetime


class InventoryBase(BaseModel):
    product_id: str
    product_name: str
    stock: int = Field(ge=0, default=0)


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    stock: int = Field(ge=0)


class DeductStockRequest(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, description="扣减数量，必须大于0")


class InventoryResponse(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
