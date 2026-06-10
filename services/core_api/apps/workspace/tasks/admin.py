from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assignee', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'ai_generated')
    search_fields = ('title', 'project__name', 'assignee__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
