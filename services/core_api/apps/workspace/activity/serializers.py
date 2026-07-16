from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ('id', 'action', 'entity_type', 'entity_id', 'metadata', 'user_email', 'created_at')

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None
