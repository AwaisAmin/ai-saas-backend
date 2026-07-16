from apps.workspace.activity.tasks import log_activity

def queue_activity(org, user, action: str, entity_type: str, entity_id=None, metadata: dict = None) -> None:
    log_activity.delay(
        organization_id=str(org.id),
        user_id=str(user.id),
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        metadata=metadata or {},
    )
