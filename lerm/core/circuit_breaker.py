"""
LERM v5 - Circuit Breaker Module
Per-model circuit breaker with CLOSED / OPEN / HALF_OPEN states.
Integrates with Prometheus metrics for observability.
"""

import time


class ModelCircuitBreaker:
    """Isolated circuit breaker for a single model backend."""

    STATE_CLOSED = 0
    STATE_OPEN = 1
    STATE_HALF_OPEN = 2

    def __init__(self, model_name: str, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.model_name = model_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.state = self.STATE_CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time: float | None = None
        self.total_requests = 0

    def can_execute(self) -> bool:
        """Check if requests can pass through the breaker."""
        if self.state == self.STATE_CLOSED:
            return True
        if self.state == self.STATE_OPEN:
            # Check if recovery timeout has elapsed
            if self.last_failure_time is not None:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self.state = self.STATE_HALF_OPEN
                    self._report_state()
            return self.state == self.STATE_HALF_OPEN
        # HALF_OPEN: allow one probe request
        return True

    def record_success(self):
        """Record a successful request."""
        self.failures = 0
        self.successes += 1

        if self.state == self.STATE_HALF_OPEN:
            # Recovery successful
            self.state = self.STATE_CLOSED

        self._report_state()
        self._report_health()

    def record_failure(self):
        """Record a failed request."""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.state == self.STATE_HALF_OPEN:
            # Probe failed, back to OPEN immediately
            self.state = self.STATE_OPEN
        elif self.failures >= self.failure_threshold:
            self.state = self.STATE_OPEN

        self._report_state()
        self._report_failures()

        # Import here to avoid circular imports at module level
        from core.metrics_collector import CIRCUIT_BREAKER_FAILURES
        CIRCUIT_BREAKER_FAILURES.labels(model=self.model_name).inc()

    def _report_state(self):
        from core.metrics_collector import CIRCUIT_BREAKER_STATE
        CIRCUIT_BREAKER_STATE.labels(model=self.model_name).set(self.state)

    def _report_failures(self):
        pass  # Failure counter incremented in record_failure

    def _report_health(self):
        """Report health score based on recent success/failure ratio."""
        from core.metrics_collector import MODEL_HEALTH
        # Simple health: 1.0 if CLOSED, 0.5 if HALF_OPEN, 0.0 if OPEN
        if self.state == self.STATE_CLOSED:
            score = 1.0
        elif self.state == self.STATE_HALF_OPEN:
            score = 0.5
        else:
            score = 0.0
        MODEL_HEALTH.labels(model=self.model_name).set(score)

    def get_state(self) -> dict:
        """Get current breaker state as dict."""
        state_names = {0: "CLOSED", 1: "OPEN", 2: "HALF_OPEN"}
        return {
            "model": self.model_name,
            "state": state_names.get(self.state, "UNKNOWN"),
            "failures": self.failures,
            "successes": self.successes,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "last_failure_time": self.last_failure_time,
        }


class CircuitBreakerManager:
    """Manages per-model circuit breakers."""

    def __init__(self, default_threshold: int = 5, default_timeout: float = 30.0):
        self.breakers: dict[str, ModelCircuitBreaker] = {}
        self.default_threshold = default_threshold
        self.default_timeout = default_timeout

    def get_breaker(self, model_name: str) -> ModelCircuitBreaker:
        """Get or create a circuit breaker for the given model."""
        if model_name not in self.breakers:
            self.breakers[model_name] = ModelCircuitBreaker(
                model_name,
                failure_threshold=self.default_threshold,
                recovery_timeout=self.default_timeout,
            )
            # Report initial state
            self.breakers[model_name]._report_state()
            self.breakers[model_name]._report_health()
        return self.breakers[model_name]

    def get_all_states(self) -> dict:
        """Get all breaker states."""
        return {
            name: breaker.get_state()
            for name, breaker in self.breakers.items()
        }

    def configure(self, model_name: str, failure_threshold: int = None, recovery_timeout: float = None):
        """Configure a specific model's breaker parameters."""
        breaker = self.get_breaker(model_name)
        if failure_threshold is not None:
            breaker.failure_threshold = failure_threshold
        if recovery_timeout is not None:
            breaker.recovery_timeout = recovery_timeout
        return breaker.get_state()


# Global singleton
circuit_manager = CircuitBreakerManager()
