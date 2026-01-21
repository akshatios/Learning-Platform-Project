from fastapi import APIRouter
from Login.LoginRoutes import router as login_router
from course.courseRoute import router as course_router

api_router = APIRouter()

api_router.include_router(login_router, tags=["Authentication"])
api_router.include_router(course_router, tags=["Courses"])