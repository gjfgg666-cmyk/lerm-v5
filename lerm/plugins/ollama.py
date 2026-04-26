import requests


class OllamaPlugin:
    def __init__(self):
        self.base_url = "http://localhost:11434/api"

    async def generate(self, messages: list):
        prompt = messages[-1]["content"]
        resp = requests.post(
            f"{self.base_url}/generate",
            json={"model": "qwen3:1.7b", "prompt": prompt, "stream": False}
        )
        return resp.json()
