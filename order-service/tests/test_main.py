import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


def create_test_app():
    app = FastAPI(title="Order Service Test", version="1.0.0")

    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "order-service"}

    @app.get("/metrics")
    def metrics():
        return "# HELP test_metric Test metric\n# TYPE test_metric gauge\ntest_metric 1.0\n"

    @app.post("/orders")
    def create_order(product_id: str, product_name: str, quantity: int, unit_price: int):
        if not product_id:
            raise HTTPException(status_code=422, detail="product_id is required")
        if quantity <= 0:
            raise HTTPException(status_code=422, detail="quantity must be positive")
        return {
            "order_id": "TEST123",
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": quantity * unit_price,
            "status": "created",
            "created_at": "2024-01-01T00:00:00"
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
    assert data["service"] == "order-service"


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "test_metric" in response.text


def test_create_order_success(client):
    response = client.post("/orders", params={
        "product_id": "PROD001",
        "product_name": "Test Product",
        "quantity": 1,
        "unit_price": 1000
    })
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "TEST123"
    assert data["quantity"] == 1


def test_create_order_missing_product_id(client):
    response = client.post("/orders", params={
        "product_name": "Test Product",
        "quantity": 1,
        "unit_price": 1000
    })
    assert response.status_code == 422


def test_create_order_invalid_quantity(client):
    response = client.post("/orders", params={
        "product_id": "PROD001",
        "product_name": "Test Product",
        "quantity": -1,
        "unit_price": 1000
    })
    assert response.status_code == 422
