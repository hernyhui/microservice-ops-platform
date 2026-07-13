import uuid
from sqlalchemy import Column, String, Integer, DateTime, func
from .database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(64), unique=True, index=True, nullable=False)
    product_id = Column(String(64), index=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="created")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
