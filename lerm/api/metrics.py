from fastapi import APIRouter
from prometheus_client import generate_latest

router = APIRouter()

@router.get("/metrics")
def metrics():
    return generate_latest()
