import time
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, get_db, Base
from .models import Inventory
from .schemas import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    DeductStockRequest,
)
from .redis_client import (
    get_stock_from_cache,
    set_stock_to_cache,
    decrement_stock_in_cache,
    delete_stock_cache,
)
from .metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    DEDUCT_STOCK_TOTAL,
    STOCK_QUERY_TOTAL,
    metrics_response,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Service", version="1.0.0")


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
    return {"status": "healthy", "service": "inventory-service"}


@app.get("/metrics")
async def get_metrics():
    return metrics_response()


@app.get("/inventory/{product_id}", response_model=InventoryResponse)
async def get_inventory(product_id: str, db: Session = Depends(get_db)):
    cached_stock = get_stock_from_cache(product_id)
    if cached_stock is not None:
        STOCK_QUERY_TOTAL.labels(source="cache").inc()
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if inventory:
            inventory.stock = cached_stock
            return inventory

    STOCK_QUERY_TOTAL.labels(source="database").inc()
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="库存记录不存在")

    set_stock_to_cache(product_id, inventory.stock)
    return inventory


@app.post("/inventory", response_model=InventoryResponse)
async def create_inventory(item: InventoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该商品库存已存在")

    inventory = Inventory(
        product_id=item.product_id,
        product_name=item.product_name,
        stock=item.stock,
    )
    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    set_stock_to_cache(item.product_id, item.stock)
    return inventory


@app.put("/inventory/{product_id}", response_model=InventoryResponse)
async def update_inventory(product_id: str, item: InventoryUpdate, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="库存记录不存在")

    inventory.stock = item.stock
    db.commit()
    db.refresh(inventory)

    set_stock_to_cache(product_id, item.stock)
    return inventory


@app.post("/inventory/deduct")
async def deduct_stock(request: DeductStockRequest, db: Session = Depends(get_db)):
    product_id = request.product_id
    quantity = request.quantity

    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        DEDUCT_STOCK_TOTAL.labels(product_id=product_id, result="not_found").inc()
        raise HTTPException(status_code=404, detail="库存记录不存在")

    cached_stock = get_stock_from_cache(product_id)
    if cached_stock is not None and cached_stock < quantity:
        DEDUCT_STOCK_TOTAL.labels(product_id=product_id, result="insufficient").inc()
        raise HTTPException(status_code=400, detail="库存不足")

    if inventory.stock < quantity:
        DEDUCT_STOCK_TOTAL.labels(product_id=product_id, result="insufficient").inc()
        raise HTTPException(status_code=400, detail="库存不足")

    inventory.stock -= quantity
    db.commit()
    db.refresh(inventory)

    if cached_stock is not None:
        decrement_stock_in_cache(product_id, quantity)
    else:
        set_stock_to_cache(product_id, inventory.stock)

    DEDUCT_STOCK_TOTAL.labels(product_id=product_id, result="success").inc()
    return {
        "success": True,
        "product_id": product_id,
        "remaining_stock": inventory.stock,
        "deducted_quantity": quantity,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.service_port, reload=True)
