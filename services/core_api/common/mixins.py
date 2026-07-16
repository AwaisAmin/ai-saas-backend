from rest_framework.exceptions import NotFound, PermissionDenied

from apps.core.organizations.models import Membership, Organization
from common.constants import ADMIN_ROLES


class OrganizationScopedMixin:
    def get_organization(self) -> Organization:
        slug = self.kwargs.get('slug')
        try:
            return Organization.objects.get(slug=slug, is_active=True)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found")

    def get_membership(self, organization: Organization = None) -> Membership:
        if organization is None:
            organization = self.get_organization()
        try:
            return Membership.objects.get(
                user=self.request.user,
                organization=organization,
            )
        except Membership.DoesNotExist:
            raise PermissionDenied("You are not a member of this organization")

    def require_admin(self, membership: Membership, message: str = "Only owner or admin can perform this action") -> None:
        if membership.role not in ADMIN_ROLES:
            raise PermissionDenied(message)
