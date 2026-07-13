import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "order-service"


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200


def test_create_order_missing_product_id():
    response = client.post("/orders", json={
        "product_name": "Test Product",
        "quantity": 1,
        "unit_price": 1000
    })
    assert response.status_code == 422


def test_create_order_missing_quantity():
    response = client.post("/orders", json={
        "product_id": "PROD001",
        "product_name": "Test Product",
        "unit_price": 1000
    })
    assert response.status_code == 422
