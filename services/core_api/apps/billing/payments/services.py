import logging
from .providers.base import get_payment_provider, WebhookEvent
from apps.billing.subscriptions.models import Subscription
from apps.core.organizations.models import Organization

logger = logging.getLogger(__name__)

class PaymentService:
    @staticmethod
    def create_checkout_session(org: Organization, plan: str, interval: str) -> str:
        provider = get_payment_provider()

        success_url = f"{__import__('os').getenv('FRONTEND_URL', 'http://localhost:3000')}/billing/success"
        cancel_url = f"{__import__('os').getenv('FRONTEND_URL', 'http://localhost:3000')}/billing/cancel"

        session = provider.create_checkout_session(
            org_slug=org.slug,
            plan=plan,
            interval=interval,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        logger.info(f"Checkout session created: org={org.slug} plan={plan} interval={interval}")
        return session.url

    @staticmethod
    def process_webhook(payload: bytes, signature: str) -> None:
        provider = get_payment_provider()
        event = provider.handle_webhook(payload, signature)

        if not event.event_type:
            return

        if event.event_type == "checkout.session.completed":
            PaymentService._activate_subscription(event)

        elif event.event_type == "customer.subscription.deleted":
            PaymentService._cancel_subscription(event)

        elif event.event_type == "invoice.payment_failed":
            PaymentService._mark_past_due(event)

    @staticmethod
    def _activate_subscription(event: WebhookEvent) -> None:
        try:
            subscription = Subscription.objects.get(
                organization__slug=event.customer_id
            )
        except Subscription.DoesNotExist:
            logger.error(f"Subscription not found for customer: {event.customer_id}")
            return

        subscription.plan = event.plan
        subscription.status = Subscription.StatusChoices.ACTIVE
        subscription.stripe_customer_id = event.customer_id
        subscription.stripe_subscription_id = event.subscription_id
        subscription.save()

        logger.info(f"Subscription activated: {event.customer_id} → {event.plan}")

    @staticmethod
    def _cancel_subscription(event: WebhookEvent) -> None:
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=event.subscription_id
            )
        except Subscription.DoesNotExist:
            logger.error(f"Subscription not found: {event.subscription_id}")
            return

        subscription.plan = Subscription.PlanChoices.FREE
        subscription.status = Subscription.StatusChoices.CANCELLED
        subscription.save()

        logger.info(f"Subscription cancelled: {event.subscription_id}")

    @staticmethod
    def _mark_past_due(event: WebhookEvent) -> None:
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=event.subscription_id
            )
        except Subscription.DoesNotExist:
            logger.error(f"Subscription not found: {event.subscription_id}")
            return

        subscription.status = Subscription.StatusChoices.PAST_DUE
        subscription.save()

        logger.info(f"Subscription past due: {event.subscription_id}")
