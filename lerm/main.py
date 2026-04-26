from fastapi import FastAPI
from api.gateway import router as chat_router
from api.metrics import router as metrics_router
from api.circuit import router as circuit_router
from api.control import router as control_router

app = FastAPI(title="LERM v5", version="v1")

# 挂载 V1 冻结 API
app.include_router(chat_router)      # /v1/chat/completions
app.include_router(metrics_router)    # /metrics
app.include_router(circuit_router)    # /circuit/state
app.include_router(control_router)    # /control/policy

@app.get("/")
def root():
    return {"name": "LERM v5", "stage": "final", "spec": "frozen"}
