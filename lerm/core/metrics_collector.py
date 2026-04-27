"""
LERM v5 - Metrics Collector Module
Prometheus custom metrics for AI inference gateway observability.
All metrics are auto-registered on import.
"""

from prometheus_client import Counter, Histogram, Gauge

# --- Request Metrics ---
REQUESTS_TOTAL = Counter(
    "lerm_requests_total",
    "Total requests processed by the gateway",
    ["model", "status"]  # status: success | error | rejected
)

REQUEST_DURATION_SECONDS = Histogram(
    "lerm_request_duration_seconds",
    "Request processing duration in seconds",
    ["model"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

ACTIVE_REQUESTS = Gauge(
    "lerm_active_requests",
    "Number of requests currently being processed"
)

# --- Error Metrics ---
ERRORS_TOTAL = Counter(
    "lerm_errors_total",
    "Total errors by model and error type",
    ["model", "error_type"]  # error_type: timeout | rate_limit | crash | invalid_response
)

# --- Circuit Breaker Metrics ---
CIRCUIT_BREAKER_STATE = Gauge(
    "lerm_circuit_breaker_state",
    "Circuit breaker state per model (0=CLOSED, 1=OPEN, 2=HALF_OPEN)",
    ["model"]
)

CIRCUIT_BREAKER_FAILURES = Counter(
    "lerm_circuit_breaker_failures_total",
    "Total circuit breaker failure events",
    ["model"]
)

CIRCUIT_BREAKER_RECOVERIES = Counter(
    "lerm_circuit_breaker_recoveries_total",
    "Total circuit breaker recovery events (OPEN -> CLOSED)",
    ["model"]
)

# --- Health Metrics ---
MODEL_HEALTH = Gauge(
    "lerm_model_health",
    "Model health score (0=unhealthy, 1=healthy)",
    ["model"]
)
