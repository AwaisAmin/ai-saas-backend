from pydantic import BaseModel as PydanticModel
from .models import Subscription
from apps.organizations.models import Organization

PLAN_LIMITS = {
    'free': {
        'max_projects': 3,
        'max_members': 5,
        'max_ai_calls_per_day': 10,
    },
    'pro': {
        'max_projects': None,      # Unlimited
        'max_members': 50,
        'max_ai_calls_per_day': 100,
    },
    'enterprise': {
        'max_projects': None,      # Unlimited
        'max_members': None,       # Unlimited
        'max_ai_calls_per_day': None,  # Unlimited
    },
}

class SubscriptionService:
    @staticmethod
    def get_or_create(organization: Organization) -> Subscription:
        subscription, _ = Subscription.objects.get_or_create(
            organization=organization,
            defaults={'plan': Subscription.PlanChoices.FREE}
        )
        return subscription

    @staticmethod
    def can_create_project(organization: Organization) -> tuple[bool, str]:
        subscription = SubscriptionService.get_or_create(organization)
        limits = PLAN_LIMITS[subscription.plan]

        if limits['max_projects'] is None:
            return True, ""

        from apps.projects.models import Project
        current_count = Project.objects.filter(
            organization=organization,
            status='active',
        ).count()

        if current_count >= limits['max_projects']:
            return False, f"Free plan allows only {limits['max_projects']} projects. Upgrade to Pro."

        return True, ""

    @staticmethod
    def can_invite_member(organization: Organization) -> tuple[bool, str]:
        subscription = SubscriptionService.get_or_create(organization)
        limits = PLAN_LIMITS[subscription.plan]

        if limits['max_members'] is None:
            return True, ""

        from apps.organizations.models import Membership
        current_count = Membership.objects.filter(
            organization=organization,
        ).count()

        if current_count >= limits['max_members']:
            return False, f"Free plan allows only {limits['max_members']} members. Upgrade to Pro."

        return True, ""

    @staticmethod
    def can_use_ai(organization: Organization) -> tuple[bool, str]:
        subscription = SubscriptionService.get_or_create(organization)
        limits = PLAN_LIMITS[subscription.plan]

        if limits['max_ai_calls_per_day'] is None:
            return True, ""

        from django.utils import timezone
        from apps.activity.models import ActivityLog

        today_ai_calls = ActivityLog.objects.filter(
            organization=organization,
            action='ai_call',
            created_at__date=timezone.now().date(),
        ).count()

        if today_ai_calls >= limits['max_ai_calls_per_day']:
            return False, f"Daily AI calls limit ({limits['max_ai_calls_per_day']}) reached. Upgrade to Pro or try tomorrow."

        return True, ""
