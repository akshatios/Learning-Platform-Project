from fastapi import APIRouter
from auth.register import router as register_router
from auth.login import router as login_router
from auth.logout import router as logout_router
from auth.user_stats import router as stats_router
from auth.email_verify import router as email_router
from auth.user_management import router as user_mgmt_router
from course.courseRoute import router as course_router
from payment.paymentRoute import router as payment_router

api_router = APIRouter()

api_router.include_router(register_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(login_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(logout_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(stats_router, prefix="/auth", tags=["User Stats"])
api_router.include_router(email_router, prefix="/auth", tags=["Email Verification"])
api_router.include_router(user_mgmt_router, prefix="/users", tags=["User Management"])
api_router.include_router(course_router, tags=["Courses"])
api_router.include_router(payment_router, tags=["Payment"])