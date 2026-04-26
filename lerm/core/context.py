"""
LERM v5 - Core Context Module
Manages request context and routing metadata.
"""


class RequestContext:
    def __init__(self):
        self.request_id = ""
        self.model = ""
        self.start_time = None
        self.metadata = {}

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "model": self.model,
            "metadata": self.metadata
        }
