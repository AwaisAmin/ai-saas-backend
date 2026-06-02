from django.contrib import admin
from .models import Organization, Membership

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'plan', 'is_active', 'created_at')
    list_filter = ('plan', 'is_active')
    search_fields = ('name', 'slug')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'joined_at')
    list_filter = ('role',)
    search_fields = ('user__email', 'organization__name')
    readonly_fields = ('id', 'joined_at')
