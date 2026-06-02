from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'owner', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'organization__name', 'owner__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
