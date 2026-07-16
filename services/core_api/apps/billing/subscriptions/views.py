from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from apps.core.organizations.models import Membership
from apps.workspace.projects.models import Project
from common.constants import PLAN_LIMITS
from common.mixins import OrganizationScopedMixin
from common.response import success_response

from .constants import PLANS_DATA
from .serializers import SubscriptionSerializer
from .services import SubscriptionService


class PlansView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request):
        return success_response(data=PLANS_DATA, message="Plans retrieved")


class SubscriptionDetailView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str):
        org = self.get_organization()
        self.get_membership(org)

        subscription = SubscriptionService.get_or_create(org)
        limits = PLAN_LIMITS[subscription.plan]

        data = {
            "subscription": SubscriptionSerializer(subscription).data,
            "limits": {
                "max_projects":         limits["max_projects"] or "Unlimited",
                "max_members":          limits["max_members"] or "Unlimited",
                "max_ai_calls_per_day": limits["max_ai_calls_per_day"] or "Unlimited",
            },
            "usage": {
                "projects": org.projects.filter(status=Project.StatusChoices.ACTIVE).count(),
                "members":  org.memberships.filter(status=Membership.StatusChoices.ACTIVE).count(),
            },
        }

        return success_response(data=data)
