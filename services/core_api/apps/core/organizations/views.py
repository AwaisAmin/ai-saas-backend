from django.core.cache import cache
from django.utils import timezone
from django.utils.text import slugify
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.billing.subscriptions.services import SubscriptionService
from apps.core.users.tasks import send_invite_email
from apps.workspace.activity.models import ActivityLog
from common.activity import queue_activity
from common.mixins import OrganizationScopedMixin
from common.response import error_response, format_errors, success_response

from .models import Membership, Organization, PendingInvite
from .serializers import (
    BulkInviteSerializer,
    InviteMemberSerializer,
    MemberSerializer,
    OrganizationCreateSerializer,
    OrganizationSerializer,
    PendingInviteSerializer,
    UpdateMemberRoleSerializer,
)
from .services import CreateOrgInput, InviteMemberInput, OrganizationService

class OrganizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        cache_key = f"user:{request.user.id}:orgs"
        cached = cache.get(cache_key)
        if cached:
            return success_response(data=cached, message="Organizations retrieved")

        memberships = OrganizationService.get_user_organizations(request.user)
        data = [
            {**OrganizationSerializer(m.organization).data, 'my_role': m.role}
            for m in memberships
        ]
        cache.set(cache_key, data, timeout=300)
        return success_response(data=data, message="Organizations retrieved")

    def post(self, request: Request):
        serializer = OrganizationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")

        inp = CreateOrgInput(
            name=serializer.validated_data['name'],
            logo_url=serializer.validated_data.get('logo_url', ''),
            purpose=serializer.validated_data.get('purpose', ''),
            size=serializer.validated_data.get('size', ''),
            color=serializer.validated_data.get('color', ''),
            slug=serializer.validated_data.get('slug', ''),
            owner_id=str(request.user.id),
        )
        org = OrganizationService.create(inp)

        request.user.onboarding_step = request.user.OnboardingStep.ORG_CREATED
        request.user.save(update_fields=['onboarding_step', 'updated_at'])

        cache.delete(f"user:{request.user.id}:orgs")
        return success_response(data=OrganizationSerializer(org).data, message="Organization created", status=201)


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
        self.require_admin(membership, "Only owner or admin can update the organization")

        serializer = OrganizationCreateSerializer(org, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")

        updated_org = serializer.save()
        cache.delete(f"org:{slug}")
        cache.delete(f"user:{request.user.id}:orgs")
        return success_response(data=OrganizationSerializer(updated_org).data, message="Organization updated")

    def delete(self, request: Request, slug: str):
        org = self.get_organization()
        try:
            OrganizationService.deactivate(organization=org, requesting_user=request.user)
            cache.delete(f"org:{slug}")
            cache.delete(f"user:{request.user.id}:orgs")
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
        self.require_admin(membership, "Only owner or admin can invite members")

        serializer = InviteMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")

        can_invite, _ = SubscriptionService.can_invite_member(org)

        try:
            inp = InviteMemberInput(
                organization_id=str(org.id),
                email=serializer.validated_data['email'],
                role=serializer.validated_data['role'],
                invited_by_id=str(request.user.id),
            )
            pending_invite = OrganizationService.invite_member(inp, plan_allows=can_invite)
            send_invite_email.delay(
                invited_email=inp.email,
                org_name=org.name,
                role=inp.role,
                invite_token=str(pending_invite.token),
                inviter_name=request.user.get_full_name() or request.user.email,
            )
            return success_response(
                data=PendingInviteSerializer(pending_invite).data,
                message="Invite sent",
                status=201,
            )
        except ValueError as e:
            return error_response(message=str(e))

class MemberDetailView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, slug: str, membership_id: str):
        org = self.get_organization()
        membership = self.get_membership(org)
        self.require_admin(membership, "Only owner or admin can change roles")

        serializer = UpdateMemberRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")

        try:
            updated = OrganizationService.update_member_role(
                membership_id=str(membership_id),
                new_role=serializer.validated_data['role'],
                organization=org,
            )
            queue_activity(
                org=org, user=request.user,
                action=ActivityLog.ActionChoices.MEMBER_ROLE_CHANGED,
                entity_type=ActivityLog.EntityTypeChoices.MEMBERSHIP,
                entity_id=membership_id,
                metadata={'new_role': serializer.validated_data['role']},
            )
            return success_response(data=MemberSerializer(updated).data, message="Role updated successfully")
        except ValueError as e:
            return error_response(message=str(e))

    def delete(self, request: Request, slug: str, membership_id: str):
        org = self.get_organization()
        membership = self.get_membership(org)
        self.require_admin(membership, "Only owner or admin can remove members")

        try:
            OrganizationService.remove_member(
                membership_id=str(membership_id),
                requesting_user=request.user,
                organization=org,
            )
            queue_activity(
                org=org, user=request.user,
                action=ActivityLog.ActionChoices.MEMBER_REMOVED,
                entity_type=ActivityLog.EntityTypeChoices.MEMBERSHIP,
                entity_id=membership_id,
                metadata={},
            )
            return success_response(message="Member removed successfully")
        except ValueError as e:
            return error_response(message=str(e))

class BulkInviteView(OrganizationScopedMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, slug: str):
        org = self.get_organization()
        membership = self.get_membership(org)
        self.require_admin(membership, "Only owner or admin can invite members")

        serializer = BulkInviteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=format_errors(serializer.errors), message="Validation failed")

        can_invite, _ = SubscriptionService.can_invite_member(org)
        invites_data = serializer.validated_data['invites']
        inviter_name = request.user.get_full_name() or request.user.email
        sent_count = 0
        skipped_count = 0

        for item in invites_data:
            inp = InviteMemberInput(
                organization_id=str(org.id),
                email=item['email'],
                role=item['role'],
                invited_by_id=str(request.user.id),
            )
            try:
                pending_invite = OrganizationService.invite_member(inp, plan_allows=can_invite)
                send_invite_email.delay(
                    invited_email=item['email'],
                    org_name=org.name,
                    role=item['role'],
                    invite_token=str(pending_invite.token),
                    inviter_name=inviter_name,
                )
                sent_count += 1
            except ValueError:
                skipped_count += 1

        if request.user.onboarding_step == request.user.OnboardingStep.ORG_CREATED:
            request.user.onboarding_step = request.user.OnboardingStep.TEAM_INVITED
            request.user.save(update_fields=['onboarding_step', 'updated_at'])

        return success_response(
            data={'sent': sent_count, 'skipped': skipped_count},
            message=f"Processed {len(invites_data)} invite(s)",
        )

class InvitePreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        token = request.GET.get('token', '').strip()
        if not token:
            return error_response(message="token is required", status=400)
        try:
            invite = PendingInvite.objects.select_related('organization', 'invited_by').get(
                token=token,
                expires_at__gt=timezone.now(),
            )
        except PendingInvite.DoesNotExist:
            return error_response(message="Invalid or expired invite", status=404)

        if invite.is_accepted:
            org = invite.organization
            return success_response(
                data={
                    'already_accepted': True,
                    'org_slug': org.slug if org.is_active else None,
                    'org_name': org.name,
                },
                message="You have already joined this organization",
            )

        return success_response(data={
            'already_accepted': False,
            'email': invite.email,
            'role': invite.role,
            'org_name': invite.organization.name,
            'org_slug': invite.organization.slug,
            'inviter_name': (
                invite.invited_by.get_full_name() if invite.invited_by else 'Someone'
            ),
        })


class InviteRespondView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        token = request.data.get('token', '').strip()
        action = request.data.get('action', '').strip()

        if not token:
            return error_response(message="token is required", status=400)
        if action not in ('accept', 'decline'):
            return error_response(message="action must be 'accept' or 'decline'", status=400)

        success, message, org_slug = OrganizationService.respond_to_invite(
            token=token, action=action, user=request.user
        )
        if not success:
            return error_response(message=message, status=400)
        return success_response(message=message, data={'org_slug': org_slug})


class SlugCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request):
        slug = slugify(request.GET.get('slug', '').strip())
        if not slug:
            return error_response(message="slug is required", status=400)
        available = not Organization.objects.filter(slug=slug, is_active=True).exists()
        return success_response(data={"available": available, "slug": slug})
