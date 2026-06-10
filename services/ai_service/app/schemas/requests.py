from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    max_tokens: Optional[int] = Field(default=1024, ge=1, le=8192)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)

class SummarizeRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)
    max_tokens: Optional[int] = Field(default=512, ge=1, le=4096)

class SuggestRequest(BaseModel):
    context: str = Field(..., min_length=1, max_length=10000)
    task_title: str = Field(..., min_length=1, max_length=500)
    max_tokens: Optional[int] = Field(default=512, ge=1, le=4096)
                          