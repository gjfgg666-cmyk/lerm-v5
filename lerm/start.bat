@echo off
echo ========================================
echo   LERM v5 - AI Inference Routing Gateway
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)
python --version

echo [2/3] Installing dependencies...
python -m pip install -r requirements.txt -q

echo [3/3] Starting LERM v5 on http://localhost:8080
echo.
echo   API Endpoints:
echo     POST /v1/chat/completions  - Chat inference
echo     GET  /metrics               - Prometheus metrics
echo     GET  /circuit/state         - Circuit breaker status
echo     POST /control/policy        - Dynamic policy
echo.
echo   Press Ctrl+C to stop
echo ========================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8080
