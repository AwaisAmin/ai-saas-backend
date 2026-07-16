import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from common.models import BaseModel
from apps.core.users.models import User

class Organization(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    logo_url = models.URLField(blank=True)

    class PlanChoices(models.TextChoices):
        FREE = 'free', 'Free'
        PRO = 'pro', 'Pro'
        BUSINESS   = 'business', 'Business'
        ENTERPRISE = 'enterprise', 'Enterprise'

    plan = models.CharField(max_length=20, choices=PlanChoices.choices, default=PlanChoices.FREE)

    class PurposeChoices(models.TextChoices):
        PRODUCT_ENGINEERING = 'product_engineering', 'Product & Engineering'
        AGENCY_CLIENTS      = 'agency_clients',      'Agency & Clients'
        MARKETING_CONTENT   = 'marketing_content',   'Marketing & Content'
        OPERATIONS_OTHER    = 'operations_other',     'Operations & Other'

    class SizeChoices(models.TextChoices):
        JUST_ME           = 'just_me',  'Just Me'
        TWO_TEN           = '2_10',     '2-10'
        ELEVEN_FIFTY      = '11_50',    '11-50'
        FIFTY_TWO_HUNDRED = '51_200',   '51-200'
        TWO_HUNDRED_PLUS  = '200_plus', '200+'

    purpose = models.CharField(max_length=30, choices=PurposeChoices.choices, blank=True)

    class ColorChoices(models.TextChoices):
        PURPLE = 'purple', 'Purple'
        RED    = 'red',    'Red'
        GREEN  = 'green',  'Green'
        YELLOW = 'yellow', 'Yellow'
        BLUE   = 'blue',   'Blue'
        PINK   = 'pink',   'Pink'

    color = models.CharField(
        max_length=20,
        choices=ColorChoices.choices,
        default=ColorChoices.PURPLE,
    )

    size    = models.CharField(max_length=20, choices=SizeChoices.choices, blank=True)
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

    class StatusChoices(models.TextChoices):
        ACTIVE  = 'active',  'Active'
        PENDING = 'pending', 'Pending'

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        db_index=True,
    )
    
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

class PendingInvite(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='pending_invites'
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=Membership.RoleChoices.choices,
        default=Membership.RoleChoices.MEMBER,
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    invited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='sent_invites'
    )
    expires_at = models.DateTimeField()
    is_accepted = models.BooleanField(default=False)

    class Meta:
        db_table = 'pending_invites'
        unique_together = ('organization', 'email')
        indexes = [
            models.Index(fields=['email'], name='idx_pending_invite_email'),
            models.Index(fields=['token'], name='idx_pending_invite_token'),
        ]

    def __str__(self) -> str:
        return f"Invite: {self.email} → {self.organization.name}"
