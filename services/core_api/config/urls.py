from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/organizations/<slug:slug>/projects/', include('apps.projects.urls')),
    path('api/v1/organizations/<slug:slug>/projects/<uuid:project_id>/tasks/', include('apps.tasks.urls')),
    path('api/v1/organizations/<slug:slug>/activity/', include('apps.activity.urls')),
    path('api/v1/organizations/<slug:slug>/subscription/', include('apps.subscriptions.urls')),
]
