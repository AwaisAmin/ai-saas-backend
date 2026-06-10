import os
from google import genai
from google.genai import types
from .base import BaseAIProvider, AIResponse

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.0-flash"

    async def generate(self, prompt: str, max_tokens: int, temperature: float) -> AIResponse:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        return AIResponse(
            content=response.text,
            provider="gemini",
            model=self.model,
            input_tokens=response.usage_metadata.prompt_token_count,
            output_tokens=response.usage_metadata.candidates_token_count,
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