from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from common.mixins import OrganizationScopedMixin
from common.response import success_response

from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ActivityLogListView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str):
        org = self.get_organization()
        self.get_membership(org)

        logs = ActivityLog.objects.filter(
            organization=org,
        ).select_related('user')[:50]

        return success_response(data=ActivityLogSerializer(logs, many=True).data)
