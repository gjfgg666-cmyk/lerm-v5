# LERM v5 — AI Inference Routing Infrastructure Primitive

> 生产级 AI 推理路由基础设施原语 | Production-grade AI inference routing kernel

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Spec: Frozen](https://img.shields.io/badge/Spec-V1-Frozen-red.svg)](docs/architecture.md)

## What is LERM v5?

LERM v5 is a **cloud-native AI inference routing infrastructure primitive**, positioned as the "Envoy of AI" — managing LLM traffic routing, circuit breaking, rate limiting, and observability in distributed systems.

| Infrastructure Primitive | Routing Layer |
|--------------------------|---------------|
| Envoy | Network traffic routing |
| **LERM v5** | **AI inference traffic routing** |

## Quick Start (No K8s Required)

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) running locally (optional, for local LLM)

### Install & Run

```bash
cd lerm
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Verify

```bash
# Health check
curl http://localhost:8080/

# Chat with local Ollama (default: qwen3:1.7b)
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "ollama", "messages": [{"role": "user", "content": "hello"}]}'

# Circuit breaker state
curl http://localhost:8080/circuit/state

# Prometheus metrics
curl http://localhost:8080/metrics

# Dynamic policy injection
curl -X POST http://localhost:8080/control/policy \
  -H "Content-Type: application/json" \
  -d '{"strategy": "least_latency", "rate_limit": 500, "timeout": "20s"}'
```

## V1 Frozen API Spec

All V1 APIs are **permanently frozen** — no breaking changes, ever.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | OpenAI-compatible inference |
| `/metrics` | GET | Prometheus metrics |
| `/circuit/state` | GET | Circuit breaker status |
| `/control/policy` | POST | Dynamic policy injection |

### Error Model

All errors include `X-LERM-Error-Type` header:

| Error Type | Meaning |
|------------|---------|
| `timeout` | Model inference timeout |
| `rate_limit` | Rate limit triggered |
| `crash` | Model service/plugin crash |
| `invalid_response` | Response protocol violation |

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  LERM v5     │────▶│   Ollama    │
│  (OpenAI    │     │  Gateway     │     │  (Local)    │
│  Compatible)│     │              │────▶│  OpenAI     │
│             │     │  ┌────────┐  │     │  (Cloud)    │
│             │     │  │Circuit │  │     │  Custom     │
│             │     │  │Breaker │  │     └─────────────┘
│             │     │  └────────┘  │
│             │     │  ┌────────┐  │
│             │     │  │ Policy │  │
│             │     │  │ Engine │  │
│             │     │  └────────┘  │
└─────────────┘     └──────────────┘
```

See [docs/architecture.md](docs/architecture.md) for full design spec.

## Deployment Modes

1. **Embedded** — Import as Python library, zero dependencies
2. **Gateway** — Standalone HTTP gateway (current default)
3. **Sidecar** — K8s sidecar injection (requires Docker/K8s)

## Project Structure

```
lerm/
├── core/           # Kernel: permanently frozen
├── plugins/        # Model plugins (Ollama, OpenAI)
├── api/            # V1 frozen API layer
├── observability/  # Prometheus + Grafana configs
├── deployment/     # Docker Compose
├── docs/           # Architecture spec
├── main.py         # Entry point
└── requirements.txt
```

## License

[MIT](LICENSE)
