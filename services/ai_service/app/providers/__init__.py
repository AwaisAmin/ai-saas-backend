import os
from .gemini import GeminiProvider
from .base import BaseAIProvider

def get_provider() -> BaseAIProvider:
    provider = os.getenv("AI_PROVIDER", "gemini").lower()

    if provider == "gemini":
        return GeminiProvider()

    raise ValueError(f"Unsupported AI_PROVIDER: '{provider}'. Supported: gemini")
