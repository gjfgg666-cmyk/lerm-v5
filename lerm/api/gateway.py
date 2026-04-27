"""
LERM v5 - Gateway API
OpenAI-compatible chat completions with full observability instrumentation.
"""

import time
from fastapi import APIRouter, Request
from core.kernel import kernel
from core.metrics_collector import (
    REQUESTS_TOTAL,
    REQUEST_DURATION_SECONDS,
    ERRORS_TOTAL,
    ACTIVE_REQUESTS,
)
from core.circuit_breaker import circuit_manager

router = APIRouter()


def classify_error(exc: Exception) -> str:
    """Classify exception into LERM canonical error types."""
    msg = str(exc).lower()
    if "timeout" in msg or "timed out" in msg:
        return "timeout"
    if "rate" in msg or "429" in msg or "quota" in msg:
        return "rate_limit"
    if "connection" in msg or "refused" in msg or "unreachable" in msg:
        return "crash"
    return "invalid_response"


def resolve_model_name(model: str) -> str:
    """Resolve user-provided model name to actual backend model for metrics."""
    if not model or model == "auto":
        return "auto"
    if model.startswith("ollama"):
        # Use the model name as-is, or default to qwen3:1.7b
        parts = model.split(":", 1)
        return parts[1] if len(parts) > 1 else "qwen3:1.7b"
    return model


@router.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    model = body.get("model", "ollama")
    messages = body.get("messages", [])

    # Resolve model name for metrics and circuit breaker
    metrics_model = resolve_model_name(model)
    breaker = circuit_manager.get_breaker(metrics_model)

    # Circuit breaker check
    if not breaker.can_execute():
        REQUESTS_TOTAL.labels(model=metrics_model, status="rejected").inc()
        return {
            "error": "circuit_open",
            "detail": f"Model '{metrics_model}' circuit breaker is OPEN. Requests are rejected.",
            "X-LERM-Error-Type": "crash",
        }

    # Instrument request lifecycle
    ACTIVE_REQUESTS.inc()
    start_time = time.monotonic()

    try:
        resp = await kernel.route(model, messages)
        breaker.record_success()

        duration = time.monotonic() - start_time
        REQUESTS_TOTAL.labels(model=metrics_model, status="success").inc()
        REQUEST_DURATION_SECONDS.labels(model=metrics_model).observe(duration)

        # Inject LERM metadata into response
        if isinstance(resp, dict):
            resp["X-LERM-Model"] = metrics_model
            resp["X-LERM-Duration-Ms"] = round(duration * 1000, 2)

        return resp

    except Exception as exc:
        breaker.record_failure()
        duration = time.monotonic() - start_time

        error_type = classify_error(exc)
        REQUESTS_TOTAL.labels(model=metrics_model, status="error").inc()
        ERRORS_TOTAL.labels(model=metrics_model, error_type=error_type).inc()
        REQUEST_DURATION_SECONDS.labels(model=metrics_model).observe(duration)

        return {
            "error": str(exc),
            "X-LERM-Error-Type": error_type,
            "X-LERM-Model": metrics_model,
            "X-LERM-Duration-Ms": round(duration * 1000, 2),
        }

    finally:
        ACTIVE_REQUESTS.dec()
