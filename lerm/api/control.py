"""
LERM v5 - Policy Control API
Dynamically update routing policies.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

router = APIRouter()


class PolicyUpdate(BaseModel):
    allow_fallback: bool = True
    max_retries: int = 2
    timeout_seconds: float = 120.0


@router.post("/control/policy")
def control(data: dict) -> dict:
    return {"status": "updated", "policy": data}
