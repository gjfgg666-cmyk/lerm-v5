# LERM v5 — Production-Grade AI Inference Routing Infrastructure

![Stage: Frozen](https://img.shields.io/badge/stage-frozen-blue)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

## Quick Start

`powershell
cd D:\projects\lerm-v5\lerm
pip install -r requirements.txt
python main.py
`

## API Documentation

**Swagger UI** — Live interactive docs at: http://localhost:8080/docs

| Endpoint | Method | Description |
|----------|--------|-------------|
| / | GET | Project info |
| /v1/chat/completions | POST | OpenAI-compatible inference proxy |
| /metrics | GET | Prometheus metrics |
| /circuit/state | GET | Circuit breaker status |
| /control/policy | POST | Hot-inject routing policy |

## Architecture

- **Core** — kernel (route engine), circuit_breaker, policy, context
- **API** — FastAPI with 5 frozen endpoints
- **Plugins** — Ollama adapter, OpenAI adapter
- **Observability** — Prometheus + Grafana
- **Deployment** — Docker Compose

## Local Ollama Test

`powershell
ollama run qwen3:1.7b
curl -X POST http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"qwen3:1.7b\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}"
`

---

Released as **v5.0.0** — https://github.com/gjfgg666-cmyk/lerm-v5/releases/tag/v5.0.0