from django.db import models
from django.utils.text import slugify
from common.models import BaseModel
from apps.users.models import User

class Organization(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    logo_url = models.URLField(blank=True)

    class PlanChoices(models.TextChoices):
        FREE = 'free', 'Free'
        PRO = 'pro', 'Pro'
        ENTERPRISE = 'enterprise', 'Enterprise'

    plan = models.CharField(max_length=20, choices=PlanChoices.choices, default=PlanChoices.FREE)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'organizations'
        indexes = [
            models.Index(fields=['slug'], name='idx_org_slug'),
            models.Index(fields=['is_active'], name='idx_org_active'),
        ]
    
    def __str__(self) -> str:
        return self.name
    
class Membership(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')

    class RoleChoices(models.TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
        VIEWER = 'viewer', 'Viewer'
    
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'memberships'
        unique_together = ('user', 'organization')
        indexes = [
            models.Index(fields=['user'], name='idx_membership_user'),
            models.Index(fields=['organization'], name='idx_membership_org'),
            models.Index(fields=['role'], name='idx_membership_role'),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.organization.name} ({self.role})"
