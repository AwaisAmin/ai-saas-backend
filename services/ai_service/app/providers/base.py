from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int

class BaseAIProvider(ABC):

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int, temperature: float) -> AIResponse:
        pass

    @abstractmethod
    async def summarize(self, content: str, max_tokens: int) -> AIResponse:
        pass

    @abstractmethod
    async def suggest(self, context: str, task_title: str, max_tokens: int) -> AIResponse:
        pass
