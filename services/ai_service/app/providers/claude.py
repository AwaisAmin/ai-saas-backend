import os
import anthropic
from .base import BaseAIProvider, AIResponse

class ClaudeProvider(BaseAIProvider):
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-8"

    async def generate(self, prompt: str, max_tokens: int, temperature: float) -> AIResponse:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return AIResponse(
            content=message.content[0].text,
            provider="claude",
            model=self.model,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
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
