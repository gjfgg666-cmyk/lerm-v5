from fastapi import APIRouter, Request
from core.kernel import kernel
from core.circuit_breaker import circuit

router = APIRouter()

@router.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    model = body.get("model", "ollama")
    messages = body.get("messages", [])

    try:
        resp = await kernel.route(model, messages)
        circuit.record_success()
        return resp
    except Exception as e:
        circuit.record_failure()
        return {
            "error": str(e),
            "X-LERM-Error-Type": "timeout | crash | rate_limit | invalid_response"
        }
