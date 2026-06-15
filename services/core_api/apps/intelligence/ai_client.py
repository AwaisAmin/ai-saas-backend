import httpx
import os

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

async def generate(prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AI_SERVICE_URL}/api/v1/ai/generate",
            json={"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

async def summarize(content: str, max_tokens: int = 512) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AI_SERVICE_URL}/api/v1/ai/summarize",
            json={"content": content, "max_tokens": max_tokens},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

async def suggest(task_title: str, context: str, max_tokens: int = 512) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AI_SERVICE_URL}/api/v1/ai/suggest",
            json={"task_title": task_title, "context": context, "max_tokens": max_tokens},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()