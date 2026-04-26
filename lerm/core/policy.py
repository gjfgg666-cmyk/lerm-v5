class Policy:
    def __init__(self):
        self.strategy = "least_latency"
        self.rate_limit = 1000
        self.timeout = "30s"

    def update(self, data: dict):
        self.strategy = data.get("strategy", self.strategy)
        self.rate_limit = data.get("rate_limit", self.rate_limit)
        self.timeout = data.get("timeout", self.timeout)
        return self.get()

    def get(self):
        return {
            "strategy": self.strategy,
            "rate_limit": self.rate_limit,
            "timeout": self.timeout
        }


policy = Policy()
