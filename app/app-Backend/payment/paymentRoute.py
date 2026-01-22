from fastapi import APIRouter
from payment.views.payment_handler import (
    create_checkout_session,
    handle_webhook,
    verify_session_payment,
    get_payment_status
)
from payment.views.setup_payment import create_setup_intent, process_payment_with_setup

router = APIRouter(prefix="/payment", tags=["Payment"])

# Stripe Checkout Session routes
router.add_api_route("/create-checkout-session", create_checkout_session, methods=["POST"])
router.add_api_route("/webhook", handle_webhook, methods=["POST"])
router.add_api_route("/verify-session", verify_session_payment, methods=["POST"])
router.add_api_route("/status/{payment_id}", get_payment_status, methods=["GET"])

# Setup Intent routes (optional)
router.add_api_route("/setup-intent", create_setup_intent, methods=["POST"])
router.add_api_route("/process-with-setup", process_payment_with_setup, methods=["POST"])
