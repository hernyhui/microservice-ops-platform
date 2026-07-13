from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

REQUEST_COUNT = Counter(
    "order_requests_total",
    "Total number of order service requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "order_request_duration_seconds",
    "Order service request latency in seconds",
    ["endpoint"]
)

ORDER_CREATE_TOTAL = Counter(
    "order_create_total",
    "Total number of order creation operations",
    ["result"]
)

INVENTORY_CALL_TOTAL = Counter(
    "order_inventory_call_total",
    "Total number of inventory service calls",
    ["operation", "result"]
)


def metrics_response():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
