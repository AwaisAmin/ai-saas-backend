import logging
logger = logging.getLogger(__name__)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from common.response import success_response, error_response
from apps.core.organizations.models import Organization, Membership
from apps.billing.subscriptions.services import SubscriptionService
from apps.workspace.activity.models import ActivityLog
from .ai_client import generate, summarize, suggest
import asyncio

def get_org_and_check_access(request, org_slug):
    try:
        org = Organization.objects.get(slug=org_slug, is_active=True)
    except Organization.DoesNotExist:
        return None, None, error_response("Organization not found", status=404)

    is_member = Membership.objects.filter(
        organization=org, user=request.user
    ).exists()
    if not is_member:
        return None, None, error_response("Access denied", status=403)

    allowed, message = SubscriptionService.can_use_ai(org)
    if not allowed:
        return None, None, error_response(message, status=403)

    return org, None, None


class GenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        org_slug = request.data.get("org_slug")
        prompt = request.data.get("prompt")

        if not org_slug or not prompt:
            return error_response("org_slug and prompt are required", status=400)

        org, _, err = get_org_and_check_access(request, org_slug)
        if err:
            return err

        max_tokens = request.data.get("max_tokens", 1024)
        temperature = request.data.get("temperature", 0.7)
        result = asyncio.run(generate(prompt, max_tokens, temperature))

        ActivityLog.objects.create(
            organization=org,
            user=request.user,
            action=ActivityLog.ActionChoices.AI_CALL,
            entity_type=ActivityLog.EntityTypeChoices.AI,
            metadata={"prompt": prompt[:100], "endpoint": "generate"},
        )

        logger.info(f"AI generate called by user={request.user.id} org={org.slug}")

        return success_response(result["data"], message="Generated successfully")

class SummarizeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        org_slug = request.data.get("org_slug")
        content = request.data.get("content")

        if not org_slug or not content:
            return error_response("org_slug and content are required", status=400)

        org, _, err = get_org_and_check_access(request, org_slug)
        if err:
            return err

        max_tokens = request.data.get("max_tokens", 512)
        result = asyncio.run(summarize(content, max_tokens))

        ActivityLog.objects.create(
            organization=org,
            user=request.user,
            action=ActivityLog.ActionChoices.AI_CALL,
            entity_type=ActivityLog.EntityTypeChoices.AI,
            metadata={"endpoint": "summarize"},
        )

        logger.info(f"AI summarize called by user={request.user.id} org={org.slug}")

        return success_response(result["data"], message="Summarized successfully")

class SuggestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        org_slug = request.data.get("org_slug")
        task_title = request.data.get("task_title")
        context = request.data.get("context")

        if not org_slug or not task_title or not context:
            return error_response("org_slug, task_title and context are required", status=400)

        org, _, err = get_org_and_check_access(request, org_slug)
        if err:
            return err

        max_tokens = request.data.get("max_tokens", 512)
        result = asyncio.run(suggest(task_title, context, max_tokens))

        ActivityLog.objects.create(
            organization=org,
            user=request.user,
            action=ActivityLog.ActionChoices.AI_CALL,
            entity_type=ActivityLog.EntityTypeChoices.AI,
            metadata={"task_title": task_title[:100], "endpoint": "suggest"},
        )

        logger.info(f"AI suggest called by user={request.user.id} org={org.slug}")

        return success_response(result["data"], message="Suggestions generated successfully")
