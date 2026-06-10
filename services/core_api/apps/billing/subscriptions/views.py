from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from common.response import success_response, error_response
from common.mixins import OrganizationScopedMixin
from .models import Subscription
from .serializers import SubscriptionSerializer
from .services import SubscriptionService, PLAN_LIMITS

class SubscriptionDetailView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str):
        org = self.get_organization()
        self.get_membership(org)

        subscription = SubscriptionService.get_or_create(org)
        limits = PLAN_LIMITS[subscription.plan]

        data = {
            'subscription': SubscriptionSerializer(subscription).data,
            'limits': {
                'max_projects': limits['max_projects'] or 'Unlimited',
                'max_members': limits['max_members'] or 'Unlimited',
                'max_ai_calls_per_day': limits['max_ai_calls_per_day'] or 'Unlimited',
            },
            'usage': {
                'projects': org.projects.filter(status='active').count(),
                'members': org.memberships.count(),
            }
        }

        return success_response(data=data)
