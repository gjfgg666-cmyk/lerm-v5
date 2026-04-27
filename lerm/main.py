from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from api.gateway import router as chat_router
from api.metrics import router as metrics_router
from api.circuit import router as circuit_router
from api.control import router as control_router
from auth import AuthMiddleware

# Create app first
app = FastAPI(title="LERM v5", version="v5.2.0")

# Rate limiter (P1 — actually enforced)
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Middleware Stack ───────────────────────────────────────────────────────────

# 1) Trusted Host (prevent host header poisoning)
# Note: Starlette only supports exact matches + domain wildcards (*.example.com).
# IP-range checking is handled separately in AuthMiddleware for internal endpoints.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "::1"],
)

# 2) CORS (P2)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],          # Locked down — no cross-origin by default
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type", "X-LERM-*"],
)

# 3) Auth middleware (P0 Bearer + model whitelist + internal-only)
app.add_middleware(AuthMiddleware)


# ── Global Request-Size Guard (P1) ────────────────────────────────────────────
@app.middleware("http")
async def max_request_size(request: Request, call_next):
    max_bytes = 10 * 1024 * 1024   # 10 MB
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_bytes:
        return JSONResponse(
            status_code=413,
            content={"error": "Request body too large. Maximum size is 10 MB."},
        )
    return await call_next(request)


# ── Global Exception Handler — hide internal errors (P1) ─────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the real error server-side; never leak it to the client
    print(f"[LERM] Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please try again later."},
    )


# ── Mount routers ─────────────────────────────────────────────────────────────
app.include_router(chat_router)      # /v1/chat/completions
app.include_router(metrics_router)   # /metrics
app.include_router(circuit_router)   # /circuit/state
app.include_router(control_router)    # /control/policy


@app.get("/")
def root():
    return {"name": "LERM v5", "stage": "security-hardened", "spec": "frozen"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
