from fastapi import HTTPException, Form
from pydantic import BaseModel
from core.database import courses_collection, db
from helperFunction.jwt_helper import verify_token
from core.config import STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
from bson import ObjectId
import stripe
from datetime import datetime

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Create payments collection
payments_collection = db.payments

class SetupResponse(BaseModel):
    setup_intent_id: str
    client_secret: str
    publishable_key: str

async def create_setup_intent(
    token: str = Form(...),
    course_id: str = Form(...),
    student_id: str = Form(...)
):
    try:
        # Verify token
        payload = verify_token(token)
        
        if payload.get("user_id") != student_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get course details
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Create Setup Intent for card collection
        setup_intent = stripe.SetupIntent.create(
            payment_method_types=["card"],
            metadata={
                "course_id": course_id,
                "student_id": student_id,
                "amount": str(int(course["price"] * 100))
            }
        )
        
        return SetupResponse(
            setup_intent_id=setup_intent["id"],
            client_secret=setup_intent["client_secret"],
            publishable_key=STRIPE_PUBLISHABLE_KEY
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup intent creation failed: {str(e)}")

async def process_payment_with_setup(
    token: str = Form(...),
    setup_intent_id: str = Form(...),
    student_id: str = Form(...)
):
    try:
        # Verify token
        payload = verify_token(token)
        
        if payload.get("user_id") != student_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Retrieve Setup Intent
        setup_intent = stripe.SetupIntent.retrieve(setup_intent_id)
        
        print(f"Setup Intent Status: {setup_intent['status']}")
        
        if setup_intent["status"] not in ["succeeded", "requires_action"]:
            raise HTTPException(status_code=400, detail=f"Card setup status: {setup_intent['status']}")
        
        # Handle requires_action status
        if setup_intent["status"] == "requires_action":
            raise HTTPException(status_code=400, detail="Additional authentication required")
        
        # Get payment method and course details
        payment_method_id = setup_intent["payment_method"]
        course_id = setup_intent["metadata"]["course_id"]
        amount_cents = int(setup_intent["metadata"]["amount"])
        
        # Create and confirm payment intent with the saved payment method
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            payment_method=payment_method_id,
            confirmation_method="automatic",
            confirm=True
        )
        
        if payment_intent["status"] == "succeeded":
            # Store payment record
            payment_data = {
                "stripe_payment_intent_id": payment_intent["id"],
                "course_id": ObjectId(course_id),
                "student_id": ObjectId(student_id),
                "amount": amount_cents / 100,
                "amount_cents": amount_cents,
                "currency": "usd",
                "status": "completed",
                "created_at": datetime.utcnow(),
                "completed_at": datetime.utcnow()
            }
            
            await payments_collection.insert_one(payment_data)
            
            # Auto-enroll student
            from course.views.enrollment import enroll_course_after_payment
            await enroll_course_after_payment(course_id, student_id)
            
            return {
                "message": "Payment successful and course enrolled",
                "status": "success",
                "payment_intent_id": payment_intent["id"]
            }
        else:
            raise HTTPException(status_code=400, detail=f"Payment failed: {payment_intent['status']}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")