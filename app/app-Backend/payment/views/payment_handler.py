from fastapi import HTTPException, Form
from pydantic import BaseModel
from core.database import courses_collection, db
from helperFunction.jwt_helper import verify_token
from core.config import STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
from bson import ObjectId
import stripe
from datetime import datetime

# Create payments collection
payments_collection = db.payments

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

class PaymentResponse(BaseModel):
    payment_id: str
    client_secret: str
    amount: int
    currency: str
    status: str
    stripe_publishable_key: str

async def create_payment_order(
    token: str = Form(...),
    course_id: str = Form(...),
    student_id: str = Form(...)
):
    try:
        # Verify token
        payload = verify_token(token)
        
        # Check if token user matches student_id
        if payload.get("user_id") != student_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get course details
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Convert price to cents (Stripe uses smallest currency unit)
        amount_cents = int(course["price"] * 100)
        
        # Create Stripe PaymentIntent with explicit configuration
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            payment_method_types=["card"],
            capture_method="automatic",
            confirmation_method="automatic",
            metadata={
                "course_id": course_id,
                "student_id": student_id,
                "course_title": course["title"]
            }
        )
        
        # Store payment record
        payment_data = {
            "stripe_payment_intent_id": payment_intent["id"],
            "course_id": ObjectId(course_id),
            "student_id": ObjectId(student_id),
            "amount": course["price"],
            "amount_cents": amount_cents,
            "currency": "usd",
            "status": "created",
            "created_at": datetime.utcnow()
        }
        
        result = await payments_collection.insert_one(payment_data)
        
        return PaymentResponse(
            payment_id=str(result.inserted_id),
            client_secret=payment_intent["client_secret"],
            amount=amount_cents,
            currency="usd",
            status="created",
            stripe_publishable_key=STRIPE_PUBLISHABLE_KEY
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment order creation failed: {str(e)}")

async def verify_payment(
    token: str = Form(...),
    payment_intent_id: str = Form(...),
    student_id: str = Form(...)
):
    try:
        # Verify token
        payload = verify_token(token)
        
        # Check if token user matches student_id
        if payload.get("user_id") != student_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Retrieve PaymentIntent from Stripe
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.InvalidRequestError as e:
            if "No such payment_intent" in str(e):
                raise HTTPException(
                    status_code=404, 
                    detail=f"Payment intent '{payment_intent_id}' not found. Please create a new payment order first."
                )
            raise HTTPException(status_code=400, detail=f"Invalid payment intent: {str(e)}")
        
        if payment_intent["status"] != "succeeded":
            raise HTTPException(
                status_code=400, 
                detail=f"Payment not completed. Current status: {payment_intent['status']}"
            )
        
        # Find payment record
        payment = await payments_collection.find_one({"stripe_payment_intent_id": payment_intent_id})
        if not payment:
            raise HTTPException(
                status_code=404, 
                detail="Payment record not found in database. Please contact support."
            )
        
        # Update payment status
        await payments_collection.update_one(
            {"_id": payment["_id"]},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        # Auto-enroll student in course after successful payment
        from course.views.enrollment import enroll_course_after_payment
        await enroll_course_after_payment(str(payment["course_id"]), student_id)
        
        return {
            "message": "Payment verified and course enrolled successfully",
            "status": "success",
            "payment_intent_id": payment_intent_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")

async def get_payment_status(payment_id: str, token: str = Form(...)):
    try:
        # Verify token
        verify_token(token)
        
        # Get payment status
        payment = await payments_collection.find_one({"_id": ObjectId(payment_id)})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {
            "payment_id": str(payment["_id"]),
            "stripe_payment_intent_id": payment["stripe_payment_intent_id"],
            "amount": payment["amount"],
            "status": payment["status"],
            "created_at": payment["created_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment status: {str(e)}")