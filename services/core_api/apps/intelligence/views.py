from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from common.response import success_response, error_response
from .ai_client import generate, summarize, suggest
import asyncio

class GenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        prompt = request.data.get("prompt")
        if not prompt:
            return error_response("prompt is required", status=400)

        max_tokens = request.data.get("max_tokens", 1024)
        temperature = request.data.get("temperature", 0.7)

        result = asyncio.run(generate(prompt, max_tokens, temperature))
        return success_response(result["data"], message="Generated successfully")

class SummarizeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        content = request.data.get("content")
        if not content:
            return error_response("content is required", status=400)

        max_tokens = request.data.get("max_tokens", 512)

        result = asyncio.run(summarize(content, max_tokens))
        return success_response(result["data"], message="Summarized successfully")

class SuggestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        task_title = request.data.get("task_title")
        context = request.data.get("context")

        if not task_title or not context:
            return error_response("task_title and context are required", status=400)

        max_tokens = request.data.get("max_tokens", 512)

        result = asyncio.run(suggest(task_title, context, max_tokens))
        return success_response(result["data"], message="Suggestions generated successfully")
