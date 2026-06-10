from django.db import models
from common.models import BaseModel
from apps.core.users.models import User
from apps.core.organizations.models import Organization

class ActivityLog(BaseModel):
    class ActionChoices(models.TextChoices):
        # Task actions
        TASK_CREATED = 'task_created', 'Task Created'
        TASK_UPDATED = 'task_updated', 'Task Updated'
        TASK_DELETED = 'task_deleted', 'Task Deleted'
        TASK_ASSIGNED = 'task_assigned', 'Task Assigned'
        TASK_STATUS_CHANGED = 'task_status_changed', 'Task Status Changed'
        # Project actions
        PROJECT_CREATED = 'project_created', 'Project Created'
        PROJECT_UPDATED = 'project_updated', 'Project Updated'
        PROJECT_DELETED = 'project_deleted', 'Project Deleted'
        PROJECT_ARCHIVED = 'project_archived', 'Project Archived'
        # Member actions
        MEMBER_INVITED = 'member_invited', 'Member Invited'
        MEMBER_REMOVED = 'member_removed', 'Member Removed'
        MEMBER_ROLE_CHANGED = 'member_role_changed', 'Member Role Changed'
        # Org actions
        ORG_UPDATED = 'org_updated', 'Organization Updated'

    class EntityTypeChoices(models.TextChoices):
        TASK = 'task', 'Task'
        PROJECT = 'project', 'Project'
        MEMBERSHIP = 'membership', 'Membership'
        ORGANIZATION = 'organization', 'Organization'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='activity_logs',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs',
    )
    action = models.CharField(max_length=50, choices=ActionChoices.choices)
    entity_type = models.CharField(max_length=20, choices=EntityTypeChoices.choices)
    entity_id = models.UUIDField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization'], name='idx_activity_org'),
            models.Index(fields=['user'], name='idx_activity_user'),
            models.Index(fields=['action'], name='idx_activity_action'),
            models.Index(fields=['entity_type', 'entity_id'], name='idx_activity_entity'),
        ]

    def __str__(self):
        return f"{self.user} — {self.action} ({self.organization})"
