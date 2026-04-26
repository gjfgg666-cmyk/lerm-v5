import os
import requests


class OpenAIPlugin:
    def __init__(self):
        self.key = os.getenv("OPENAI_API_KEY", "")

    async def generate(self, messages: list):
        headers = {"Authorization": f"Bearer {self.key}"}
        data = {"model": "gpt-3.5-turbo", "messages": messages}
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers, json=data
        )
        return resp.json()
