from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_due_date_reminders():
    from .models import Task
    from apps.users.tasks import send_reminder_email

    tomorrow = timezone.now().date() + timedelta(days=1)

    due_tasks = Task.objects.filter(
        due_date=tomorrow,
        status__in=['todo', 'in_progress', 'in_review'],
    ).select_related('assignee', 'project')

    for task in due_tasks:
        if task.assignee and task.assignee.email:
            send_reminder_email.delay(
                user_email=task.assignee.email,
                first_name=task.assignee.first_name,
                task_title=task.title,
                project_name=task.project.name,
                due_date=str(task.due_date),
            )
