from fastapi import HTTPException, Form, Request
from pydantic import BaseModel
from core.database import courses_collection, db
from helperFunction.jwt_helper import verify_token
from bson import ObjectId
import stripe
from datetime import datetime
from core.config import STRIPE_SECRET_KEY

# Create payments collection
payments_collection = db.payments

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
    status: str

async def create_checkout_session(
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
        
        # Create line items for Stripe Checkout
        line_items = [{
            "price_data": {
                "currency": "usd",
                "unit_amount": int(course["price"] * 100),  # Convert to cents
                "product_data": {
                    "name": course["title"],
                    "description": course["description"],
                    "images": [course.get("thumbnail", "https://via.placeholder.com/300x200")]
                }
            },
            "quantity": 1
        }]
        
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="http://127.0.0.1:5500/app/app-Frontend/index.html?session_id={CHECKOUT_SESSION_ID}&payment=success",
            cancel_url="http://127.0.0.1:5500/app/app-Frontend/index.html?payment=cancelled",
            metadata={
                "course_id": course_id,
                "student_id": student_id,
                "course_title": course["title"]
            }
        )
        
        # Store checkout session in database
        payment_data = {
            "stripe_session_id": checkout_session["id"],
            "course_id": ObjectId(course_id),
            "student_id": ObjectId(student_id),
            "amount": course["price"],
            "amount_cents": int(course["price"] * 100),
            "currency": "usd",
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        await payments_collection.insert_one(payment_data)
        
        return CheckoutResponse(
            checkout_url=checkout_session["url"],
            session_id=checkout_session["id"],
            status="created"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout session creation failed: {str(e)}")

async def verify_session_payment(
    session_id: str = Form(...),
    token: str = Form(...)
):
    try:
        # Verify token
        verify_token(token)
        
        # Retrieve session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status != "paid":
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Update local payment record
        payment = await payments_collection.find_one({"stripe_session_id": session_id})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment record not found")
        
        if payment["status"] != "completed":
            await payments_collection.update_one(
                {"_id": payment["_id"]},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow(),
                        "stripe_payment_intent_id": session.payment_intent
                    }
                }
            )
            
            # Auto-enroll student
            from course.views.enrollment import enroll_course_after_payment
            await enroll_course_after_payment(
                str(payment["course_id"]), 
                str(payment["student_id"])
            )
        
        return {
            "message": "Payment verified and course enrolled successfully",
            "status": "success",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session verification failed: {str(e)}")

async def handle_webhook(request: Request):
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # Verify webhook signature (in production, use webhook secret)
        event = stripe.Webhook.construct_event(
            payload, sig_header, "whsec_your_webhook_secret_here"
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Update payment status
            await payments_collection.update_one(
                {"stripe_session_id": session['id']},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow(),
                        "stripe_payment_intent_id": session.get('payment_intent')
                    }
                }
            )
            
            # Get payment record for enrollment
            payment = await payments_collection.find_one({"stripe_session_id": session['id']})
            if payment:
                # Auto-enroll student
                from course.views.enrollment import enroll_course_after_payment
                await enroll_course_after_payment(
                    str(payment["course_id"]), 
                    str(payment["student_id"])
                )
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

async def get_payment_status(payment_id: str, token: str = Form(...)):
    try:
        verify_token(token)
        payment = await payments_collection.find_one({"_id": ObjectId(payment_id)})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {
            "payment_id": str(payment["_id"]),
            "stripe_session_id": payment.get("stripe_session_id"),
            "amount": payment["amount"],
            "status": payment["status"],
            "created_at": payment["created_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment status: {str(e)}")