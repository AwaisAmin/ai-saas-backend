from rest_framework import serializers
from .models import Organization, Membership
from apps.core.users.serializers import UserSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'logo_url', 'plan', 'purpose', 'size', 'is_active', 'created_at')
        read_only_fields = ('id', 'slug', 'plan', 'is_active', 'created_at')

class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('name', 'logo_url', 'purpose', 'size')

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters")
        return value

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ('id', 'user', 'role', 'status', 'joined_at')
        read_only_fields = ('id', 'user', 'status', 'joined_at')

class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=[
            Membership.RoleChoices.ADMIN,
            Membership.RoleChoices.MEMBER,
            Membership.RoleChoices.VIEWER,
        ],
        default=Membership.RoleChoices.MEMBER,
    )

class UpdateMemberRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=[
            Membership.RoleChoices.ADMIN,
            Membership.RoleChoices.MEMBER,
            Membership.RoleChoices.VIEWER,
        ]
    )
