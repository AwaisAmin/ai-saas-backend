from rest_framework.exceptions import NotFound, PermissionDenied

from apps.core.organizations.models import Membership, Organization

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
            return Membership.objects.select_related('user', 'organization').get(
                user=self.request.user,
                organization=organization,
            )
        except Membership.DoesNotExist:
            raise PermissionDenied("You are not a member of this organization")
