from fastapi import APIRouter
from payment.views.payment_handler import create_payment_order, verify_payment, get_payment_status
from payment.views.setup_payment import create_setup_intent, process_payment_with_setup

router = APIRouter(prefix="/payment", tags=["Payment"])

router.add_api_route("/create-order", create_payment_order, methods=["POST"])
router.add_api_route("/verify-payment", verify_payment, methods=["POST"])
router.add_api_route("/status/{payment_id}", get_payment_status, methods=["GET"])

# Setup Intent routes
router.add_api_route("/setup-intent", create_setup_intent, methods=["POST"])
router.add_api_route("/process-with-setup", process_payment_with_setup, methods=["POST"])
