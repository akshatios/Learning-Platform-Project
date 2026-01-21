from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from core.config import MONGODB_URL, DB_NAME

router = APIRouter()

# MongoDB connection
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
users_collection = db['Users']
enrollments_collection = db['Enrollments']

@router.get('/students')
def get_all_students():
    """Get all students for teachers to see"""
    try:
        students = list(users_collection.find(
            {"role": "student", "email_verified": True},
            {"password": 0}  # Exclude password
        ))
        
        for student in students:
            student["_id"] = str(student["_id"])
            
            # Get enrollment count for each student
            enrollment_count = enrollments_collection.count_documents({"student_id": str(student["_id"])})
            student["enrolled_courses"] = enrollment_count
        
        return {"students": students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/teachers')
def get_all_teachers():
    """Get all teachers"""
    try:
        teachers = list(users_collection.find(
            {"role": "Teacher", "email_verified": True},
            {"password": 0}  # Exclude password
        ))
        
        for teacher in teachers:
            teacher["_id"] = str(teacher["_id"])
        
        return {"teachers": teachers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/profile/{user_id}')
def get_user_profile(user_id: str):
    """Get user profile details"""
    try:
        user = users_collection.find_one(
            {"_id": ObjectId(user_id)},
            {"password": 0}  # Exclude password
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["_id"] = str(user["_id"])
        
        # Add role-specific data
        if user["role"] == "student":
            # Get enrolled courses count
            enrollment_count = enrollments_collection.count_documents({"student_id": user_id})
            user["enrolled_courses"] = enrollment_count
            
        elif user["role"] == "Teacher":
            # Get created courses count
            from course.courseRoute import courses_collection
            course_count = courses_collection.count_documents({"teacher_id": user_id})
            user["created_courses"] = course_count
        
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))