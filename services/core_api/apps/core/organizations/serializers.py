from rest_framework import serializers

from apps.core.users.serializers import UserSerializer
from common.serializers import validate_text_field

from .models import Membership, Organization, PendingInvite

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'logo_url', 'plan', 'purpose', 'size', 'color', 'is_active', 'created_at')
        read_only_fields = ('id', 'slug', 'plan', 'is_active', 'created_at')

class OrganizationCreateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = Organization
        fields = ('name', 'logo_url', 'purpose', 'size', 'color', 'slug')

    def validate_name(self, value):
        return validate_text_field(value, "Name")

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

class PendingInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingInvite
        fields = ('id', 'email', 'role', 'token', 'expires_at', 'is_accepted', 'created_at')
        read_only_fields = fields

class BulkInviteItemSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=[
            Membership.RoleChoices.ADMIN,
            Membership.RoleChoices.MEMBER,
            Membership.RoleChoices.VIEWER,
        ],
        default=Membership.RoleChoices.MEMBER,
    )

class BulkInviteSerializer(serializers.Serializer):
    invites = BulkInviteItemSerializer(many=True)

    def validate_invites(self, value):
        if not value:
            raise serializers.ValidationError("At least one invite is required")
        if len(value) > 50:
            raise serializers.ValidationError("Maximum 50 invites per request")
        emails = [item['email'] for item in value]
        if len(emails) != len(set(emails)):
            raise serializers.ValidationError("Duplicate emails in invite list")
        return value
