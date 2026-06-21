import os
import stripe
from .base import BasePaymentProvider, CheckoutSession, WebhookEvent

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

STRIPE_PRICES = {
    'pro_monthly':      os.getenv('STRIPE_PRO_MONTHLY_PRICE_ID'),
    'pro_yearly':       os.getenv('STRIPE_PRO_YEARLY_PRICE_ID'),
    'business_monthly': os.getenv('STRIPE_BUSINESS_MONTHLY_PRICE_ID'),
    'business_yearly':  os.getenv('STRIPE_BUSINESS_YEARLY_PRICE_ID'),
}

class StripeProvider(BasePaymentProvider):
    def create_checkout_session(
        self, org_slug: str, plan: str, interval: str, success_url: str, cancel_url: str
    ) -> CheckoutSession:
        price_key = f"{plan}_{interval}"
        price_id = STRIPE_PRICES.get(price_key)

        if not price_id:
            raise ValueError(f"No Stripe price found for: {price_key}")

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"org_slug": org_slug, "plan": plan, "interval": interval},
        )
        return CheckoutSession(url=session.url, session_id=session.id)

    def handle_webhook(self, payload: bytes, signature: str) -> WebhookEvent:
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            return WebhookEvent(
                event_type=event["type"],
                customer_id=session.get("customer", ""),
                subscription_id=session.get("subscription", ""),
                plan=session["metadata"]["plan"],
                interval=session["metadata"]["interval"],
                status="active",
            )

        if event["type"] == "customer.subscription.deleted":
            sub = event["data"]["object"]
            return WebhookEvent(
                event_type=event["type"],
                customer_id=sub.get("customer", ""),
                subscription_id=sub.get("id", ""),
                plan="free",
                interval="",
                status="cancelled",
            )

        if event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            return WebhookEvent(
                event_type=event["type"],
                customer_id=invoice.get("customer", ""),
                subscription_id=invoice.get("subscription", ""),
                plan="",
                interval="",
                status="past_due",
            )

        return WebhookEvent(
            event_type=event["type"],
            customer_id="",
            subscription_id="",
            plan="",
            interval="",
            status="",
        )

    def cancel_subscription(self, subscription_id: str) -> bool:
        stripe.Subscription.cancel(subscription_id)
        return True

    def get_customer_portal_url(self, customer_id: str, return_url: str) -> str:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url
