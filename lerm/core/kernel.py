from plugins.ollama import OllamaPlugin
from plugins.openai import OpenAIPlugin


class LERMKernel:
    def __init__(self):
        self.plugins = {
            "ollama": OllamaPlugin(),
            "openai": OpenAIPlugin()
        }

    async def route(self, model: str, messages: list):
        # 极简路由：本地用 ollama，云端用 openai
        if model.startswith("ollama"):
            return await self.plugins["ollama"].generate(messages)
        return await self.plugins["openai"].generate(messages)


kernel = LERMKernel()
