import asyncio
import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.billing.subscriptions.services import SubscriptionService
from apps.core.organizations.models import Membership, Organization
from apps.workspace.activity.models import ActivityLog
from common.activity import queue_activity
from common.response import error_response, success_response

from .ai_client import generate, summarize, suggest

logger = logging.getLogger(__name__)


def _get_org_and_check_access(request, org_slug):
    try:
        org = Organization.objects.get(slug=org_slug, is_active=True)
    except Organization.DoesNotExist:
        return None, error_response(message="Organization not found", status=404)

    is_member = Membership.objects.filter(
        organization=org,
        user=request.user,
        status=Membership.StatusChoices.ACTIVE,
    ).exists()
    if not is_member:
        return None, error_response(message="Access denied", status=403)

    allowed, message = SubscriptionService.can_use_ai(org)
    if not allowed:
        return None, error_response(message=message, status=403)

    return org, None


class GenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        org_slug = request.data.get("org_slug")
        prompt = request.data.get("prompt")

        if not org_slug or not prompt:
            return error_response(message="org_slug and prompt are required", status=400)

        org, err = _get_org_and_check_access(request, org_slug)
        if err:
            return err

        result = asyncio.run(generate(prompt, request.data.get("max_tokens", 1024), request.data.get("temperature", 0.7)))
        queue_activity(org=org, user=request.user, action=ActivityLog.ActionChoices.AI_CALL,
                       entity_type=ActivityLog.EntityTypeChoices.AI, metadata={"prompt": prompt[:100], "endpoint": "generate"})
        logger.info(f"AI generate: user={request.user.id} org={org.slug}")
        return success_response(data=result["data"], message="Generated successfully")


class SummarizeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        org_slug = request.data.get("org_slug")
        content = request.data.get("content")

        if not org_slug or not content:
            return error_response(message="org_slug and content are required", status=400)

        org, err = _get_org_and_check_access(request, org_slug)
        if err:
            return err

        result = asyncio.run(summarize(content, request.data.get("max_tokens", 512)))
        queue_activity(org=org, user=request.user, action=ActivityLog.ActionChoices.AI_CALL,
                       entity_type=ActivityLog.EntityTypeChoices.AI, metadata={"endpoint": "summarize"})
        logger.info(f"AI summarize: user={request.user.id} org={org.slug}")
        return success_response(data=result["data"], message="Summarized successfully")


class SuggestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        org_slug = request.data.get("org_slug")
        task_title = request.data.get("task_title")
        context = request.data.get("context")

        if not org_slug or not task_title or not context:
            return error_response(message="org_slug, task_title and context are required", status=400)

        org, err = _get_org_and_check_access(request, org_slug)
        if err:
            return err

        result = asyncio.run(suggest(task_title, context, request.data.get("max_tokens", 512)))
        queue_activity(org=org, user=request.user, action=ActivityLog.ActionChoices.AI_CALL,
                       entity_type=ActivityLog.EntityTypeChoices.AI, metadata={"task_title": task_title[:100], "endpoint": "suggest"})
        logger.info(f"AI suggest: user={request.user.id} org={org.slug}")
        return success_response(data=result["data"], message="Suggestions generated successfully")
