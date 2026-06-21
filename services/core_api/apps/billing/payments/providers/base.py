import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class CheckoutSession:
    url: str
    session_id: str

@dataclass
class WebhookEvent:
    event_type: str
    customer_id: str
    subscription_id: str
    plan: str
    interval: str
    status: str

class BasePaymentProvider(ABC):
    @abstractmethod
    def create_checkout_session(
        self, org_slug: str, plan: str, interval: str, success_url: str, cancel_url: str
    ) -> CheckoutSession:
        pass

    @abstractmethod
    def handle_webhook(self, payload: bytes, signature: str) -> WebhookEvent:
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        pass

    @abstractmethod
    def get_customer_portal_url(self, customer_id: str, return_url: str) -> str:
        pass

def get_payment_provider() -> BasePaymentProvider:
    provider = os.getenv("PAYMENT_PROVIDER", "stripe").lower()
    if provider == "stripe":
        from .stripe import StripeProvider
        return StripeProvider()
    raise ValueError(f"Unsupported PAYMENT_PROVIDER: '{provider}'")
