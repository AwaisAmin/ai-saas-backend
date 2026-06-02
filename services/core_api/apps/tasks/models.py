from django.db import models
from common.models import BaseModel
from apps.users.models import User
from apps.projects.models import Project

class Task(BaseModel):
    class StatusChoices(models.TextChoices):
        TODO = 'todo', 'Todo'
        IN_PROGRESS = 'in_progress', 'In Progress'
        IN_REVIEW = 'in_review', 'In Review'
        DONE = 'done', 'Done'

    class PriorityChoices(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
    )
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.TODO,
    )
    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
    )
    due_date = models.DateField(null=True, blank=True)
    ai_generated = models.BooleanField(default=False)

    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project'], name='idx_task_project'),
            models.Index(fields=['assignee'], name='idx_task_assignee'),
            models.Index(fields=['status'], name='idx_task_status'),
            models.Index(fields=['priority'], name='idx_task_priority'),
            models.Index(fields=['due_date'], name='idx_task_due_date'),
            models.Index(fields=['project', 'status'], name='idx_task_project_status'),
        ]

    def __str__(self):
        return self.title
