from fastapi import APIRouter
from core.circuit_breaker import circuit

router = APIRouter()

@router.get("/circuit/state")
def state():
    return circuit.get_state()
