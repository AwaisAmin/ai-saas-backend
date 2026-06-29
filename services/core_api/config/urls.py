from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from common.views import health_check, readiness_check
from apps.billing.subscriptions.urls import plans_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('health/', health_check, name='health'),
    path('ready/', readiness_check, name='ready'),
    path('api/v1/auth/', include('apps.core.users.urls')),
    path('api/v1/organizations/', include('apps.core.organizations.urls')),
    path('api/v1/organizations/<slug:slug>/projects/', include('apps.workspace.projects.urls')),
    path('api/v1/organizations/<slug:slug>/projects/<uuid:project_id>/tasks/', include('apps.workspace.tasks.urls')),
    path('api/v1/organizations/<slug:slug>/activity/', include('apps.workspace.activity.urls')),
    path('api/v1/organizations/<slug:slug>/subscription/', include('apps.billing.subscriptions.urls')),
    path('api/v1/billing/plans/', include((plans_urlpatterns, 'billing'))),
    path('api/v1/ai/', include('apps.intelligence.urls')),
    path('api/v1/payments/', include('apps.billing.payments.urls')),
]
