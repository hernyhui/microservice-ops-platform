import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


def create_test_app():
    app = FastAPI(title="Inventory Service Test", version="1.0.0")

    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "inventory-service"}

    @app.get("/metrics")
    def metrics():
        return "# HELP test_metric Test metric\n# TYPE test_metric gauge\ntest_metric 1.0\n"

    @app.get("/inventory/{product_id}")
    def get_inventory(product_id: str):
        if product_id == "INVALID_PRODUCT":
            raise HTTPException(status_code=404, detail="Product not found")
        return {
            "product_id": product_id,
            "product_name": f"Product {product_id}",
            "stock": 100,
            "updated_at": "2024-01-01T00:00:00"
        }

    @app.post("/inventory/deduct")
    def deduct_stock(product_id: str, quantity: int):
        if not product_id:
            raise HTTPException(status_code=422, detail="product_id is required")
        if quantity <= 0:
            raise HTTPException(status_code=422, detail="quantity must be positive")
        return {
            "product_id": product_id,
            "stock": 90,
            "message": "Stock deducted successfully"
        }

    return app


@pytest.fixture
def client():
    app = create_test_app()
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "inventory-service"


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "test_metric" in response.text


def test_get_inventory_success(client):
    response = client.get("/inventory/PROD001")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "PROD001"
    assert data["stock"] == 100


def test_get_inventory_invalid_product_id(client):
    response = client.get("/inventory/INVALID_PRODUCT")
    assert response.status_code == 404


def test_deduct_stock_success(client):
    response = client.post("/inventory/deduct", params={
        "product_id": "PROD001",
        "quantity": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert data["stock"] == 90


def test_deduct_stock_missing_product_id(client):
    response = client.post("/inventory/deduct", params={
        "quantity": 1
    })
    assert response.status_code == 422


def test_deduct_stock_invalid_quantity(client):
    response = client.post("/inventory/deduct", params={
        "product_id": "PROD001",
        "quantity": -1
    })
    assert response.status_code == 422
