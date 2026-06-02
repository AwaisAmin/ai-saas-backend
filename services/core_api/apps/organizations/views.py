from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from common.response import success_response, error_response, format_errors
from common.mixins import OrganizationScopedMixin
from .models import Membership
from .serializers import (
    OrganizationSerializer,
    OrganizationCreateSerializer,
    MemberSerializer,
    InviteMemberSerializer,
    UpdateMemberRoleSerializer,
)
from .services import OrganizationService, CreateOrgInput, InviteMemberInput

ADMIN_ROLES = [Membership.RoleChoices.OWNER, Membership.RoleChoices.ADMIN]

class OrganizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        cache_key = f"user:{request.user.id}:orgs"
        cached = cache.get(cache_key)
        if cached:
            return success_response(data=cached, message="Organizations retrieved")

        orgs = OrganizationService.get_user_organizations(request.user)
        memberships = Membership.objects.filter(
            user=request.user,
            organization__in=orgs,
        ).select_related('organization')

        data = []
        for m in memberships:
            org_data = OrganizationSerializer(m.organization).data
            org_data['my_role'] = m.role
            data.append(org_data)

        cache.set(cache_key, data, timeout=300)
        return success_response(data=data, message="Organizations retrieved")

    def post(self, request: Request):
        serializer = OrganizationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                errors=format_errors(serializer.errors),
                message="Validation failed",
            )

        inp = CreateOrgInput(
            name=serializer.validated_data['name'],
            logo_url=serializer.validated_data.get('logo_url', ''),
            owner_id=str(request.user.id),
        )
        org = OrganizationService.create(inp)
        cache.delete(f"user:{request.user.id}:orgs")
        return success_response(
            data=OrganizationSerializer(org).data,
            message="Organization created",
            status=201,
        )

class OrganizationDetailView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str):
        cache_key = f"org:{slug}"
        org_data = cache.get(cache_key)

        if org_data:
            return success_response(data=org_data)

        org = self.get_organization()
        self.get_membership(org)
        org_data = OrganizationSerializer(org).data
        cache.set(cache_key, org_data, timeout=300)

        return success_response(data=org_data)

    def patch(self, request: Request, slug: str):
        org = self.get_organization()
        membership = self.get_membership(org)

        if membership.role not in ADMIN_ROLES:
            return error_response(
                message="Only owner or admin can update the organization",
                status=403,
            )

        serializer = OrganizationCreateSerializer(org, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                errors=format_errors(serializer.errors),
                message="Validation failed",
            )

        updated_org = serializer.save()
        cache.delete(f"org:{slug}")
        return success_response(
            data=OrganizationSerializer(updated_org).data,
            message="Organization updated",
        )
    
    def delete(self, request: Request, slug: str):
        org = self.get_organization()

        try:
            OrganizationService.deactivate(
                organization=org,
                requesting_user=request.user,
            )
            cache.delete(f"org:{slug}")
            return success_response(message="Organization deleted successfully")
        except ValueError as e:
            return error_response(message=str(e), status=403)

class MemberListInviteView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, slug: str):
        org = self.get_organization()
        self.get_membership(org)
        members = Membership.objects.filter(organization=org).select_related('user')
        return success_response(data=MemberSerializer(members, many=True).data)

    def post(self, request: Request, slug: str):
        org = self.get_organization()
        membership = self.get_membership(org)

        if membership.role not in ADMIN_ROLES:
            return error_response(
                message="Only owner or admin can invite members",
                status=403,
            )

        serializer = InviteMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                errors=format_errors(serializer.errors),
                message="Validation failed",
            )

        try:
            inp = InviteMemberInput(
                organization_id=str(org.id),
                email=serializer.validated_data['email'],
                role=serializer.validated_data['role'],
            )
            new_membership = OrganizationService.invite_member(inp)
            return success_response(
                data=MemberSerializer(new_membership).data,
                message="Member invited successfully",
                status=201,
            )
        except ValueError as e:
            return error_response(message=str(e))

class MemberDetailView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, slug: str, membership_id: str):
        org = self.get_organization()
        requesting_membership = self.get_membership(org)

        if requesting_membership.role not in ADMIN_ROLES:
            return error_response(
                message="Only owner or admin can change roles",
                status=403,
            )

        serializer = UpdateMemberRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                errors=format_errors(serializer.errors),
                message="Validation failed",
            )

        try:
            updated = OrganizationService.update_member_role(
                membership_id=str(membership_id),
                new_role=serializer.validated_data['role'],
                organization=org,
            )
            return success_response(
                data=MemberSerializer(updated).data,
                message="Role updated successfully",
            )
        except ValueError as e:
            return error_response(message=str(e))

    def delete(self, request: Request, slug: str, membership_id: str):
        org = self.get_organization()
        requesting_membership = self.get_membership(org)

        if requesting_membership.role not in ADMIN_ROLES:
            return error_response(
                message="Only owner or admin can remove members",
                status=403,
            )

        try:
            OrganizationService.remove_member(
                membership_id=str(membership_id),
                requesting_user=request.user,
                organization=org,
            )
            return success_response(message="Member removed successfully")
        except ValueError as e:
            return error_response(message=str(e))
