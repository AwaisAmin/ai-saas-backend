from django.db import models
from common.models import BaseModel
from apps.core.users.models import User
from apps.core.organizations.models import Organization

class Project(BaseModel):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='projects',
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_projects',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization'], name='idx_project_org'),
            models.Index(fields=['status'], name='idx_project_status'),
            models.Index(fields=['organization', 'status'], name='idx_project_org_status'),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"
