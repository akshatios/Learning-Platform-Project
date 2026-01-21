from fastapi import HTTPException, Form, Query
from pydantic import BaseModel
from core.database import courses_collection, users_collection, db
from helperFunction.jwt_helper import verify_token
from bson import ObjectId
from datetime import datetime

# Create enrollments collection
enrollments_collection = db.enrollments

class EnrollmentResponse(BaseModel):
    message: str
    enrollment_id: str

class StudentCoursesResponse(BaseModel):
    enrollments: list
    total: int

async def enroll_course(
    token: str = Form(...),
    course_id: str = Form(...),
    student_id: str = Form(...)
):
    try:
        # Verify token
        payload = verify_token(token)
        
        # Check if token user matches student_id
        if payload.get("user_id") != student_id:
            raise HTTPException(status_code=403, detail="Unauthorized to enroll for this student")
        
        # Check if student exists
        student = await users_collection.find_one({"_id": ObjectId(student_id), "role": "student"})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if already enrolled
        existing = await enrollments_collection.find_one({
            "course_id": ObjectId(course_id),
            "student_id": ObjectId(student_id)
        })
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")
        
        # Create enrollment
        enrollment_doc = {
            "course_id": ObjectId(course_id),
            "student_id": ObjectId(student_id),
            "course_title": course["title"],
            "student_name": student["name"],
            "enrolled_at": datetime.utcnow(),
            "progress": 0,
            "completed": False
        }
        
        result = await enrollments_collection.insert_one(enrollment_doc)
        
        # Update course enrolled count
        await courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$inc": {"enrolled_count": 1}}
        )
        
        return EnrollmentResponse(
            message="Enrolled successfully",
            enrollment_id=str(result.inserted_id)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")

async def get_student_courses(student_id: str):
    try:
        enrollments_cursor = enrollments_collection.find({"student_id": ObjectId(student_id)})
        enrollments = await enrollments_cursor.to_list(length=None)
        
        enrollment_list = []
        for enrollment in enrollments:
            enrollment_list.append({
                "id": str(enrollment["_id"]),
                "course_id": str(enrollment["course_id"]),
                "course_title": enrollment["course_title"],
                "enrolled_at": enrollment["enrolled_at"].isoformat(),
                "progress": enrollment["progress"],
                "completed": enrollment["completed"]
            })
        
        return StudentCoursesResponse(
            enrollments=enrollment_list,
            total=len(enrollment_list)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student courses: {str(e)}")

async def enroll_course_after_payment(course_id: str, student_id: str):
    try:
        users_collection = db.Users
        
        # Check if student exists
        student = await users_collection.find_one({"_id": ObjectId(student_id), "role": "student"})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if already enrolled
        existing = await enrollments_collection.find_one({
            "course_id": ObjectId(course_id),
            "student_id": ObjectId(student_id)
        })
        if existing:
            return {"message": "Already enrolled"}
        
        # Create enrollment
        enrollment_doc = {
            "course_id": ObjectId(course_id),
            "student_id": ObjectId(student_id),
            "course_title": course["title"],
            "student_name": student["name"],
            "enrolled_at": datetime.utcnow(),
            "progress": 0,
            "completed": False,
            "payment_status": "completed"
        }
        
        await enrollments_collection.insert_one(enrollment_doc)
        
        # Update course enrolled count
        await courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$inc": {"enrolled_count": 1}}
        )
        
        return {"message": "Enrolled successfully"}
        
    except Exception as e:
        print(f"Error in enrollment after payment: {e}")
        raise