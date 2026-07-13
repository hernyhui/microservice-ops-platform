import time
import uuid
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, get_db, Base
from .models import Order
from .schemas import OrderCreate, OrderResponse
from .inventory_client import deduct_inventory
from .metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ORDER_CREATE_TOTAL,
    INVENTORY_CALL_TOTAL,
    metrics_response,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service", version="1.0.0")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    endpoint = request.url.path
    method = request.method

    try:
        response = await call_next(request)
        status = str(response.status_code)
    except Exception as e:
        status = "500"
        raise e
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        if endpoint not in ("/health", "/metrics"):
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

    return response


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}


@app.get("/metrics")
async def get_metrics():
    return metrics_response()


def generate_order_no() -> str:
    return f"ORD{uuid.uuid4().hex[:16].upper()}"


@app.post("/orders", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    try:
        result = await deduct_inventory(order_data.product_id, order_data.quantity)
        INVENTORY_CALL_TOTAL.labels(operation="deduct", result="success").inc()
    except Exception as e:
        INVENTORY_CALL_TOTAL.labels(operation="deduct", result="failed").inc()
        ORDER_CREATE_TOTAL.labels(result="inventory_failed").inc()
        raise HTTPException(status_code=400, detail=f"库存扣减失败: {str(e)}")

    order_no = generate_order_no()
    total_amount = order_data.unit_price * order_data.quantity

    order = Order(
        order_no=order_no,
        product_id=order_data.product_id,
        product_name=order_data.product_name,
        quantity=order_data.quantity,
        total_amount=total_amount,
        status="paid",
    )

    try:
        db.add(order)
        db.commit()
        db.refresh(order)
    except Exception as e:
        ORDER_CREATE_TOTAL.labels(result="db_error").inc()
        raise HTTPException(status_code=500, detail=f"订单创建失败: {str(e)}")

    ORDER_CREATE_TOTAL.labels(result="success").inc()
    return order


@app.get("/orders/{order_no}", response_model=OrderResponse)
async def get_order(order_no: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@app.get("/orders", response_model=list[OrderResponse])
async def list_orders(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, reload=True)
