"""
LERM v5 - Metrics API
Exposes Prometheus metrics. Already protected by AuthMiddleware (internal-only).
"""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest

router = APIRouter()


@router.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return generate_latest()
