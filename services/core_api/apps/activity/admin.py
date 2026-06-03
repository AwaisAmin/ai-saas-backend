from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'entity_type', 'user', 'organization', 'created_at')
    list_filter = ('action', 'entity_type')
    search_fields = ('user__email', 'organization__name')
    readonly_fields = ('id', 'organization', 'user', 'action', 'entity_type', 'entity_id', 'metadata', 'created_at')
