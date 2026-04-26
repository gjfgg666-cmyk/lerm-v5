class CircuitBreaker:
    def __init__(self):
        self.state = "CLOSED"
        self.failure = 0

    def record_success(self):
        self.failure = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure += 1
        if self.failure >= 5:
            self.state = "OPEN"

    def get_state(self):
        return {"state": self.state, "failures": self.failure}


circuit = CircuitBreaker()
