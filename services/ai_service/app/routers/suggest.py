from fastapi import APIRouter, HTTPException
from app.schemas.requests import SuggestRequest
from app.providers import get_provider

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

@router.post("/suggest")
async def suggest(request: SuggestRequest):
    try:
        provider = get_provider()
        result = await provider.suggest(
            context=request.context,
            task_title=request.task_title,
            max_tokens=request.max_tokens,
        )
        return {
            "success": True,
            "message": "Suggestions generated successfully",
            "data": {
                "suggestions": result.content,
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
