from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.core.users.urls')),
    path('api/v1/organizations/', include('apps.core.organizations.urls')),
    path('api/v1/organizations/<slug:slug>/projects/', include('apps.workspace.projects.urls')),
    path('api/v1/organizations/<slug:slug>/projects/<uuid:project_id>/tasks/', include('apps.workspace.tasks.urls')),
    path('api/v1/organizations/<slug:slug>/activity/', include('apps.workspace.activity.urls')),
    path('api/v1/organizations/<slug:slug>/subscription/', include('apps.billing.subscriptions.urls')),
    path('api/v1/ai/', include('apps.intelligence.urls')),
]
