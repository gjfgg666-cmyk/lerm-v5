# LERM v5 — Production-Grade AI Inference Routing Infrastructure

![Stage: Active Development](https://img.shields.io/badge/stage-active--dev-green)
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
| /circuit/state | GET | All model circuit breaker status |
| /circuit/state/{model} | GET | Single model circuit breaker details |
| /circuit/configure | POST | Runtime breaker parameter tuning |
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

## v5.1.0 — Stage 1: Production Metrics & Circuit Breaker

### What's New
- **8 custom Prometheus metrics** — request count, latency histogram, active gauge, error classification, circuit breaker state, model health
- **Per-model isolated circuit breaker** — independent CLOSED/OPEN/HALF_OPEN state per backend model
- **HALF_OPEN recovery probing** — automatic single-request probe after recovery timeout
- **Request lifecycle instrumentation** — timing, counting, model labeling, error classification, response headers (`X-LERM-Model`, `X-LERM-Duration-Ms`)
- **Runtime breaker configuration API** — tune `failure_threshold` and `recovery_timeout` without restart

### Error Classification
| Type | Description |
|------|-------------|
| timeout | Backend response timeout |
| rate_limit | 429 / rate limited |
| crash | Backend crash / connection refused |
| invalid_response | Non-JSON or malformed response |

---

Released as **v5.0.0** — https://github.com/gjfgg666-cmyk/lerm-v5/releases/tag/v5.0.0
Released as **v5.1.0** — https://github.com/gjfgg666-cmyk/lerm-v5/releases/tag/v5.1.0