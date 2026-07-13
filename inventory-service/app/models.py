from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(String(64), unique=True, index=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
