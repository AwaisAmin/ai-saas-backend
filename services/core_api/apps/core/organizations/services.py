from django.utils.text import slugify
from pydantic import BaseModel as PydanticModel
from .models import Organization, Membership
from apps.core.users.models import User

class CreateOrgInput(PydanticModel):
    name: str
    logo_url: str = ""
    owner_id: str

class InviteMemberInput(PydanticModel):
    organization_id: str
    email: str
    role: str = "member"

class OrganizationService:
    @staticmethod
    def create(data: CreateOrgInput) -> Organization:
        base_slug = slugify(data.name)
        slug = base_slug
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        org = Organization.objects.create(
            name=data.name,
            slug=slug,
            logo_url=data.logo_url,
        )
        Membership.objects.create(
            user_id=data.owner_id,
            organization=org,
            role=Membership.RoleChoices.OWNER,
        )
        return org

    @staticmethod
    def get_user_organizations(user: User):
        return (
            Organization.objects
            .filter(memberships__user=user, is_active=True)
            .order_by('-created_at')
        )

    @staticmethod
    def invite_member(data: InviteMemberInput) -> Membership:
        try:
            user = User.objects.get(email=data.email)
        except User.DoesNotExist:
            raise ValueError(f"No user found with email '{data.email}'")

        if Membership.objects.filter(user=user, organization_id=data.organization_id).exists():
            raise ValueError("User is already a member of this organization")

        return Membership.objects.create(
            user=user,
            organization_id=data.organization_id,
            role=data.role,
        )

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

        organization.is_active = False
        organization.save(update_fields=['is_active', 'updated_at'])

