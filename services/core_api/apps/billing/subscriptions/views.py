import os
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from common.response import success_response
from common.mixins import OrganizationScopedMixin
from .serializers import SubscriptionSerializer
from .services import SubscriptionService, PLAN_LIMITS

PLANS_DATA = [
    {
        "id": "free",
        "name": "Free",
        "price": {"monthly": 0, "yearly": 0},
        "price_ids": {"monthly": None, "yearly": None},
        "limits": PLAN_LIMITS["free"],
        "features": [
            "Up to 5 members",
            "3 projects",
            "10 AI actions/day",
            "Basic boards & tasks",
        ],
    },
    {
        "id": "pro",
        "name": "Pro",
        "price": {"monthly": 35, "yearly": 29},
        "price_ids": {
            "monthly": os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID"),
            "yearly":  os.getenv("STRIPE_PRO_YEARLY_PRICE_ID"),
        },
        "limits": PLAN_LIMITS["pro"],
        "features": [
            "Up to 15 members",
            "Unlimited projects",
            "100 AI actions/day",
            "Roadmaps & analytics",
            "Priority support",
        ],
    },
    {
        "id": "business",
        "name": "Business",
        "price": {"monthly": 99, "yearly": 79},
        "price_ids": {
            "monthly": os.getenv("STRIPE_BUSINESS_MONTHLY_PRICE_ID"),
            "yearly":  os.getenv("STRIPE_BUSINESS_YEARLY_PRICE_ID"),
        },
        "limits": PLAN_LIMITS["business"],
        "features": [
            "Up to 50 members",
            "Unlimited projects",
            "500 AI actions/day",
            "Automations",
            "Advanced analytics",
            "Dedicated support",
        ],
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "price": {"monthly": None, "yearly": None},
        "price_ids": {"monthly": None, "yearly": None},
        "limits": PLAN_LIMITS["enterprise"],
        "features": [
            "Unlimited members",
            "Unlimited projects",
            "2000 AI actions/day",
            "SSO & audit logs",
            "Custom integrations",
            "SLA & dedicated account manager",
        ],
    },
]

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
        from .services import PLAN_LIMITS
        limits = PLAN_LIMITS[subscription.plan]

        data = {
            "subscription": SubscriptionSerializer(subscription).data,
            "limits": {
                "max_projects":        limits["max_projects"] or "Unlimited",
                "max_members":         limits["max_members"] or "Unlimited",
                "max_ai_calls_per_day": limits["max_ai_calls_per_day"] or "Unlimited",
            },
            "usage": {
                "projects": org.projects.filter(status="active").count(),
                "members":  org.memberships.filter(status="active").count(),
            },
        }

        return success_response(data=data)
