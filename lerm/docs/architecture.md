# LERM v5 Architecture Spec

## Design Philosophy

LERM v5 is designed as a **cloud-native infrastructure primitive** for AI inference routing. It follows the same design principles as Envoy (network routing) but targets LLM inference traffic.

## Core Design Principles

1. **API Contract Freeze** — V1 APIs are permanently stable
2. **Plugin Isolation** — Each LLM backend is a separate plugin
3. **Deployment Mode Isolation** — sidecar/gateway/embedded are strictly separated
4. **Unified Error Model** — 4 canonical error types across all plugins
5. **Observable by Default** — Prometheus metrics + OpenTelemetry traces

## Component Architecture

### Kernel (core/)
The routing engine. Dispatches requests to appropriate plugins based on model prefix.

### Plugins (plugins/)
Each LLM provider is a plugin implementing `generate(messages) -> response`.
- `ollama.py` — Local LLM via Ollama REST API
- `openai.py` — Cloud LLM via OpenAI API

### API Layer (api/)
V1 frozen endpoints:
- `gateway.py` — OpenAI-compatible chat completions
- `metrics.py` — Prometheus metrics endpoint
- `circuit.py` — Circuit breaker state query
- `control.py` — Dynamic policy injection

### Circuit Breaker (core/circuit_breaker.py)
Simple state machine: CLOSED → OPEN (after 5 failures) → CLOSED (on success).

### Policy Engine (core/policy.py)
Runtime-configurable routing strategy, rate limit, and timeout.

## Error Model

| Error Type | Semantic | Recovery |
|------------|----------|----------|
| timeout | Inference exceeded timeout | Retry with different backend |
| rate_limit | API quota exceeded | Backoff + retry |
| crash | Service/plugin failure | Circuit breaker opens |
| invalid_response | Malformed response | Fallback to alternate model |

## Deployment Topology

```
Mode: Embedded
┌──────────────────────┐
│  Application Process │
│  ┌────────────────┐  │
│  │   LERM v5      │  │
│  │   (in-process) │  │
│  └────────────────┘  │
└──────────────────────┘

Mode: Gateway
┌──────────┐     ┌──────────────┐     ┌──────────┐
│ Clients  │────▶│  LERM v5 GW  │────▶│ LLM APIs │
└──────────┘     └──────────────┘     └──────────┘

Mode: Sidecar
┌──────────┐     ┌──────────┐     ┌──────────┐
│  App Pod │────▶│  LERM v5 │────▶│ LLM APIs │
└──────────┘     │ (sidecar)│     └──────────┘
                 └──────────┘
```

## Version Policy

- **V1** — Permanently frozen, no breaking changes
- **V2** — Future features, does not affect V1 deployments
