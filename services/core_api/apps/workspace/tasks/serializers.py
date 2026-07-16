from rest_framework import serializers

from common.serializers import validate_text_field

from .models import Task
from apps.core.users.serializers import UserSerializer

class TaskSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'ai_generated', 'assignee', 'created_by',
            'project', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'ai_generated', 'created_by', 'project', 'created_at', 'updated_at')

class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ('title', 'description', 'priority', 'due_date', 'assignee_id')

    def validate_title(self, value):
        return validate_text_field(value, "Title")

class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ('title', 'description', 'status', 'priority', 'due_date', 'assignee_id')

    def validate_title(self, value):
        return validate_text_field(value, "Title")

    def validate_status(self, value):
        if value not in Task.StatusChoices.values:
            raise serializers.ValidationError("Invalid status")
        return value
