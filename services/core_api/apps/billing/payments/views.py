import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.core.organizations.models import Membership, Organization
from common.response import error_response, success_response

from .services import PaymentService

logger = logging.getLogger(__name__)


class CreateCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        org_slug = request.data.get("org_slug")
        plan = request.data.get("plan")
        interval = request.data.get("interval", "monthly")

        if not org_slug or not plan:
            return error_response(message="org_slug and plan are required", status=400)

        if plan not in ["pro", "business"]:
            return error_response(message="Invalid plan. Choose: pro, business", status=400)

        if interval not in ["monthly", "yearly"]:
            return error_response(message="Invalid interval. Choose: monthly, yearly", status=400)

        try:
            org = Organization.objects.get(slug=org_slug, is_active=True)
        except Organization.DoesNotExist:
            return error_response(message="Organization not found", status=404)

        is_owner = Membership.objects.filter(
            organization=org,
            user=request.user,
            role=Membership.RoleChoices.OWNER,
        ).exists()
        if not is_owner:
            return error_response(message="Only org owner can manage billing", status=403)

        checkout_url = PaymentService.create_checkout_session(org, plan, interval)
        return success_response(data={"checkout_url": checkout_url}, message="Checkout session created")


@api_view(["POST"])
@permission_classes([AllowAny])
def stripe_webhook(request: Request):
    payload = request.body
    signature = request.headers.get("Stripe-Signature", "")

    if not signature:
        return error_response(message="Missing Stripe signature", status=400)

    try:
        PaymentService.process_webhook(payload, signature)
        return success_response(message="Webhook processed")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return error_response(message="Webhook processing failed", status=400)
