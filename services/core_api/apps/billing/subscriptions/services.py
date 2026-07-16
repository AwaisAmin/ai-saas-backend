from django.core.cache import cache
from django.utils import timezone

from .models import Subscription
from apps.core.organizations.models import Organization, Membership
from apps.workspace.projects.models import Project
from apps.workspace.activity.models import ActivityLog
from common.constants import PLAN_LIMITS

_AI_CALLS_CACHE_TTL = 60  # seconds — DB hit at most once per minute per org

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

        current_count = Project.objects.filter(
            organization=organization,
            status=Project.StatusChoices.ACTIVE,
        ).count()

        if current_count >= limits['max_projects']:
            return False, f"{subscription.plan.title()} plan allows only {limits['max_projects']} projects. Upgrade your plan."

        return True, ""

    @staticmethod
    def can_invite_member(organization: Organization) -> tuple[bool, str]:
        subscription = SubscriptionService.get_or_create(organization)
        limits = PLAN_LIMITS[subscription.plan]

        if limits['max_members'] is None:
            return True, ""

        current_count = Membership.objects.filter(
            organization=organization,
            status=Membership.StatusChoices.ACTIVE,
        ).count()

        if current_count >= limits['max_members']:
            return False, f"{subscription.plan.title()} plan allows only {limits['max_members']} members. Upgrade your plan."

        return True, ""

    @staticmethod
    def can_use_ai(organization: Organization) -> tuple[bool, str]:
        subscription = SubscriptionService.get_or_create(organization)
        limits = PLAN_LIMITS[subscription.plan]

        if limits['max_ai_calls_per_day'] is None:
            return True, ""

        cache_key = f"ai_calls:{organization.id}:{timezone.now().date()}"
        today_ai_calls = cache.get(cache_key)

        if today_ai_calls is None:
            today_ai_calls = ActivityLog.objects.filter(
                organization=organization,
                action=ActivityLog.ActionChoices.AI_CALL,
                created_at__date=timezone.now().date(),
            ).count()
            cache.set(cache_key, today_ai_calls, timeout=_AI_CALLS_CACHE_TTL)

        if today_ai_calls >= limits['max_ai_calls_per_day']:
            return False, f"Daily AI limit ({limits['max_ai_calls_per_day']} calls) reached. Upgrade your plan."

        return True, ""
