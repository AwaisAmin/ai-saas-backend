import os
from .base import BaseAIProvider
from .gemini import GeminiProvider
from .claude import ClaudeProvider
from .openai import OpenAIProvider

def get_provider() -> BaseAIProvider:
    provider = os.getenv("AI_PROVIDER", "gemini").lower()

    if provider == "gemini":
        return GeminiProvider()
    elif provider == "claude":
        return ClaudeProvider()
    elif provider == "openai":
        return OpenAIProvider()

    raise ValueError(f"Unsupported AI_PROVIDER: '{provider}'. Supported: gemini, claude, openai")
