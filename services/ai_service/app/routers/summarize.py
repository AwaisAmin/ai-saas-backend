from fastapi import APIRouter, HTTPException
from app.schemas.requests import SummarizeRequest
from app.providers import get_provider

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

@router.post("/summarize")
async def summarize(request: SummarizeRequest):
    try:
        provider = get_provider()
        result = await provider.summarize(
            content=request.content,
            max_tokens=request.max_tokens,
        )
        return {
            "success": True,
            "message": "Summarized successfully",
            "data": {
                "summary": result.content,
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
