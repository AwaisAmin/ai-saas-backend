from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework import serializers
from common.response import success_response
from common.mixins import OrganizationScopedMixin
from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ('id', 'action', 'entity_type', 'entity_id', 'metadata', 'user_email', 'created_at')

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None

class ActivityLogListView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str):
        org = self.get_organization()
        self.get_membership(org)

        logs = ActivityLog.objects.filter(
            organization=org,
        ).select_related('user')[:50]

        return success_response(data=ActivityLogSerializer(logs, many=True).data)
