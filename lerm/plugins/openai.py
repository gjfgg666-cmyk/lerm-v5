import os
import httpx


class OpenAIPlugin:
    def __init__(self):
        self.key = os.getenv("OPENAI_API_KEY", "")

    async def generate(self, messages: list) -> dict:
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        data = {"model": "gpt-3.5-turbo", "messages": messages}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers, json=data,
            )
            return resp.json()
