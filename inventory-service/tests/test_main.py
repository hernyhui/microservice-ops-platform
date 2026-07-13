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
    assert data["service"] == "inventory-service"


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200


def test_get_inventory_invalid_product_id():
    response = client.get("/inventory/INVALID_PRODUCT")
    assert response.status_code == 404


def test_deduct_stock_missing_product_id():
    response = client.post("/inventory/deduct", json={
        "quantity": 1
    })
    assert response.status_code == 422


def test_deduct_stock_missing_quantity():
    response = client.post("/inventory/deduct", json={
        "product_id": "PROD001"
    })
    assert response.status_code == 422
