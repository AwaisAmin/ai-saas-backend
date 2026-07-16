from rest_framework import serializers

from apps.core.users.serializers import UserSerializer
from common.constants import TEMPLATE_COLUMNS
from common.serializers import validate_text_field

from .models import Project, ProjectColumn

class ProjectColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectColumn
        fields = ('id', 'name', 'order')

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    columns = ProjectColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'status', 'template',
            'owner', 'organization', 'columns', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'owner', 'organization', 'template', 'columns', 'created_at', 'updated_at')

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'description', 'template')

    def validate_name(self, value):
        return validate_text_field(value, "Name")

    def validate_template(self, value):
        if value not in TEMPLATE_COLUMNS:
            raise serializers.ValidationError(f"Invalid template. Valid options: {', '.join(TEMPLATE_COLUMNS.keys())}")
        return value

class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'description', 'status')

    def validate_name(self, value):
        return validate_text_field(value, "Name")

    def validate_status(self, value):
        if value not in Project.StatusChoices.values:
            raise serializers.ValidationError("Invalid status")
        return value
