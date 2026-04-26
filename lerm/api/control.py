from fastapi import APIRouter
from core.policy import policy

router = APIRouter()

@router.post("/control/policy")
def control(data: dict):
    return policy.update(data)
