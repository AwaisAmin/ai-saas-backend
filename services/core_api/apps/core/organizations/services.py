from datetime import timedelta

from django.utils import timezone
from django.utils.text import slugify
from pydantic import BaseModel as PydanticModel

from apps.core.users.models import User
from .models import Membership, Organization, PendingInvite

class CreateOrgInput(PydanticModel):
    name: str
    logo_url: str = ""
    purpose: str = ""
    size: str = ""
    color: str = ""
    slug: str = ""
    owner_id: str

class UpdateOrgInput(PydanticModel):
    name: str | None = None
    logo_url: str | None = None
    purpose: str | None = None
    size: str | None = None

class InviteMemberInput(PydanticModel):
    organization_id: str
    email: str
    role: str = "member"
    invited_by_id: str = ""

class OrganizationService:
    @staticmethod
    def create(data: CreateOrgInput) -> Organization:
        base_slug = slugify(data.slug) if data.slug else slugify(data.name)
        slug = base_slug

        # Release slug from soft-deleted org so it can be reused
        inactive = Organization.objects.filter(slug=slug, is_active=False).first()
        if inactive:
            inactive.slug = f"{slug}-deleted-{str(inactive.id)[:8]}"
            inactive.save(update_fields=['slug', 'updated_at'])

        counter = 1
        while Organization.objects.filter(slug=slug, is_active=True).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        org = Organization.objects.create(
            name=data.name,
            slug=slug,
            logo_url=data.logo_url,
            purpose=data.purpose,
            size=data.size,
            color=data.color or Organization.ColorChoices.PURPLE,
        )
        Membership.objects.create(
            user_id=data.owner_id,
            organization=org,
            role=Membership.RoleChoices.OWNER,
            status=Membership.StatusChoices.ACTIVE,
        )
        return org

    @staticmethod
    def get_user_organizations(user: User):
        return (
            Membership.objects
            .filter(user=user, organization__is_active=True, status=Membership.StatusChoices.ACTIVE)
            .select_related('organization')
            .order_by('-organization__created_at')
        )

    @staticmethod
    def invite_member(data: InviteMemberInput, plan_allows: bool) -> PendingInvite:
        """Always creates a PendingInvite — user must explicitly accept via respond endpoint."""
        try:
            user = User.objects.get(email=data.email)
            if Membership.objects.filter(user=user, organization_id=data.organization_id).exists():
                raise ValueError("User is already a member of this organization")
        except User.DoesNotExist:
            pass

        if not plan_allows:
            raise PermissionError("Member limit reached. Upgrade your plan to invite more members.")

        return OrganizationService._upsert_pending_invite(data)

    @staticmethod
    def _upsert_pending_invite(data: InviteMemberInput) -> PendingInvite:
        expires = timezone.now() + timedelta(days=7)
        invite, created = PendingInvite.objects.get_or_create(
            organization_id=data.organization_id,
            email=data.email,
            defaults={
                'role': data.role,
                'invited_by_id': data.invited_by_id or None,
                'expires_at': expires,
            },
        )
        if not created:
            invite.role = data.role
            invite.expires_at = expires
            invite.is_accepted = False
            invite.save(update_fields=['role', 'expires_at', 'is_accepted', 'updated_at'])
        return invite

    @staticmethod
    def respond_to_invite(token: str, action: str, user: User) -> tuple[bool, str, str | None]:
        """Returns (success, message, org_slug). org_slug is set only on accept."""
        try:
            invite = PendingInvite.objects.select_related('organization').get(
                token=token,
                is_accepted=False,
                expires_at__gt=timezone.now(),
            )
        except PendingInvite.DoesNotExist:
            return False, "Invalid or expired invite", None

        if invite.email.lower() != user.email.lower():
            return False, "This invite was not sent to your email address", None

        if action == 'decline':
            invite.delete()
            return True, "Invite declined", None

        if Membership.objects.filter(user=user, organization=invite.organization).exists():
            invite.is_accepted = True
            invite.save(update_fields=['is_accepted', 'updated_at'])
            return True, "You are already a member of this organization", invite.organization.slug

        Membership.objects.create(
            user=user,
            organization=invite.organization,
            role=invite.role,
            status=Membership.StatusChoices.ACTIVE,
        )
        invite.is_accepted = True
        invite.save(update_fields=['is_accepted', 'updated_at'])
        return True, "You have joined the organization successfully", invite.organization.slug

    @staticmethod
    def activate_pending_members(organization: Organization) -> int:
        updated = Membership.objects.filter(
            organization=organization,
            status=Membership.StatusChoices.PENDING,
        ).update(status=Membership.StatusChoices.ACTIVE)
        return updated

    @staticmethod
    def update_member_role(membership_id: str, new_role: str, organization: Organization) -> Membership:
        try:
            membership = Membership.objects.select_related('user').get(
                id=membership_id,
                organization=organization,
            )
        except Membership.DoesNotExist:
            raise ValueError("Member not found")

        if membership.role == Membership.RoleChoices.OWNER:
            raise ValueError("Cannot change the owner's role")

        membership.role = new_role
        membership.save(update_fields=['role', 'updated_at'])
        return membership

    @staticmethod
    def remove_member(membership_id: str, requesting_user: User, organization: Organization) -> None:
        try:
            membership = Membership.objects.get(
                id=membership_id,
                organization=organization,
            )
        except Membership.DoesNotExist:
            raise ValueError("Member not found")

        if membership.role == Membership.RoleChoices.OWNER:
            raise ValueError("Cannot remove the owner of an organization")

        if membership.user_id == requesting_user.id:
            raise ValueError("You cannot remove yourself")

        membership.delete()

    @staticmethod
    def deactivate(organization: Organization, requesting_user: User) -> None:
        membership = Membership.objects.get(
            user=requesting_user,
            organization=organization,
        )
        if membership.role != Membership.RoleChoices.OWNER:
            raise ValueError("Only the owner can delete an organization")

        short_id = str(organization.id)[:8]
        organization.slug = f"{organization.slug}-deleted-{short_id}"
        organization.is_active = False
        organization.save(update_fields=['slug', 'is_active', 'updated_at'])
