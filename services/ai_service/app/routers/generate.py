from fastapi import APIRouter, HTTPException
from app.schemas.requests import GenerateRequest
from app.providers import get_provider

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

@router.post("/generate")
async def generate(request: GenerateRequest):
    try:
        provider = get_provider()
        result = await provider.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        return {
            "success": True,
            "message": "Generated successfully",
            "data": {
                "content": result.content,
                "provider": result.provider,
                "model": result.model,
                "usage": {
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                },
            },
            "errors": None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
