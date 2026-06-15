import os
from openai import AsyncOpenAI
from .base import BaseAIProvider, AIResponse

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    async def generate(self, prompt: str, max_tokens: int, temperature: float) -> AIResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return AIResponse(
            content=response.choices[0].message.content,
            provider="openai",
            model=self.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
        )

    async def summarize(self, content: str, max_tokens: int) -> AIResponse:
        prompt = f"Summarize the following content concisely:\n\n{content}"
        return await self.generate(prompt, max_tokens, temperature=0.3)

    async def suggest(self, context: str, task_title: str, max_tokens: int) -> AIResponse:
        prompt = (
            f"You are a project management assistant.\n"
            f"Task: {task_title}\n"
            f"Context: {context}\n\n"
            f"Provide 3 actionable suggestions to complete this task effectively."
        )
        return await self.generate(prompt, max_tokens, temperature=0.7)
