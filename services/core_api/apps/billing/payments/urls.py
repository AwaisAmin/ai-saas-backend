from django.urls import path
from .views import CreateCheckoutView, stripe_webhook

urlpatterns = [
    path('checkout/', CreateCheckoutView.as_view(), name='payment-checkout'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
]
