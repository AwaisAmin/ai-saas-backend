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

    class TemplateChoices(models.TextChoices):
        PRODUCT_SPRINT     = 'product_sprint',     'Product / Sprint'
        MARKETING_CAMPAIGN = 'marketing_campaign', 'Marketing Campaign'
        DESIGN_AGENCY      = 'design_agency',      'Design / Agency'
        BLANK              = 'blank',              'Blank Project'

    template = models.CharField(
        max_length=30,
        choices=TemplateChoices.choices,
        default=TemplateChoices.BLANK,
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

class ProjectColumn(BaseModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='columns',
    )
    name  = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'project_columns'
        ordering = ['order']
        indexes = [
            models.Index(fields=['project', 'order'], name='idx_column_project_order'),
        ]

    def __str__(self):
        return f"{self.project.name} — {self.name}"
