"""
LERM v5 - Authentication & Authorization
Bearer token auth + model name whitelist.
"""
import os
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Config
ALLOWED_MODELS = {
    "qwen3:1.7b", "qwen3:0.6b", "qwen2.5:7b", "qwen2.5:14b", "qwen2.5:32b",
    "llama3.1:8b", "llama3.2:3b", "mistral:7b", "deepseek-r1:1.5b",
    "auto", "ollama", "ollama/qwen3:1.7b",
}


def _json_response(status_code: int, detail: str) -> JSONResponse:
    """Return a JSON error response directly — avoids Starlette middleware issues."""
    return JSONResponse(status_code=status_code, content={"detail": detail})


class AuthMiddleware(BaseHTTPMiddleware):
    PROTECTED = {"/v1/chat/completions", "/circuit/configure", "/control/policy"}
    INTERNAL_ONLY = {"/metrics", "/circuit/state", "/circuit/configure", "/control/policy"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Internal-only guard
        if path in self.INTERNAL_ONLY:
            client_host = request.client.host if request.client else ""
            allow = (
                client_host in ("127.0.0.1", "localhost", "::1")
                or client_host.startswith(("10.", "172.", "192.168."))
            )
            if not allow:
                return _json_response(403, "Internal endpoints are not remotely accessible.")

        # Auth check
        if path in self.PROTECTED:
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return _json_response(401, "Missing or invalid Authorization header.")
            token = header[7:]
            expected = os.environ.get("LERM_API_KEY", "")
            if not expected or token != expected:
                return _json_response(401, "Invalid API key.")

        return await call_next(request)


def check_model(model: str) -> None:
    if model not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model}' is not in the allowed model list.",
        )
