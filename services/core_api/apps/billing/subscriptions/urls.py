from django.urls import path
from .views import SubscriptionDetailView, PlansView

urlpatterns = [
    path('', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('plans/', PlansView.as_view(), name='plans'),
]
