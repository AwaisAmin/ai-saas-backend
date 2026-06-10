from rest_framework import serializers
from .models import Project
from apps.core.users.serializers import UserSerializer

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'status',
            'owner', 'organization', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'owner', 'organization', 'created_at', 'updated_at')


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'description')

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters")
        return value


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'description', 'status')

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters")
        return value

    def validate_status(self, value):
        if value not in Project.StatusChoices.values:
            raise serializers.ValidationError("Invalid status")
        return value
