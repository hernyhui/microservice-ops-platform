from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

REQUEST_COUNT = Counter(
    "inventory_requests_total",
    "Total number of inventory service requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "inventory_request_duration_seconds",
    "Inventory service request latency in seconds",
    ["endpoint"]
)

DEDUCT_STOCK_TOTAL = Counter(
    "inventory_deduct_total",
    "Total number of stock deduction operations",
    ["product_id", "result"]
)

STOCK_QUERY_TOTAL = Counter(
    "inventory_query_total",
    "Total number of stock queries",
    ["source"]
)


def metrics_response():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
