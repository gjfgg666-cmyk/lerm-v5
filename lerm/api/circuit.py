"""
LERM v5 - Circuit Breaker API
Query and manage per-model circuit breaker states.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.circuit_breaker import circuit_manager

router = APIRouter()


class BreakerConfig(BaseModel):
    model: str
    failure_threshold: Optional[int] = None
    recovery_timeout: Optional[float] = None


@router.get("/circuit/state")
def get_state():
    return {"models": circuit_manager.get_all_states()}


@router.get("/circuit/state/{model_name}")
def get_model_state(model_name: str):
    breaker = circuit_manager.get_breaker(model_name)
    return breaker.get_state()


@router.post("/circuit/configure")
async def configure_breaker(config: BreakerConfig):
    result = circuit_manager.configure(
        model_name=config.model,
        failure_threshold=config.failure_threshold,
        recovery_timeout=config.recovery_timeout,
    )
    return {"status": "updated", **result}
