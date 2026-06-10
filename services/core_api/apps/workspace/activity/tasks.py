from celery import shared_task

@shared_task
def log_activity(organization_id: str, user_id: str, action: str,
                 entity_type: str, entity_id: str, metadata: dict = None):
    from .models import ActivityLog

    ActivityLog.objects.create(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
    )
