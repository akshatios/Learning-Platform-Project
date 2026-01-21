from datetime import datetime
from fastapi import HTTPException, UploadFile, Form
from pydantic import BaseModel
from core.database import courses_collection, db
from helperFunction.imageUpload import upload_image
from helperFunction.jwt_helper import verify_token
from bson import ObjectId

class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    thumbnail_url: str
    thumbnail_public_id: str
    price: float
    teacher_id: str
    teacher_name: str
    visible: bool
    created_date: str

async def create_course(
    token: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    teacher_id: str = Form(...),
    visible: bool = Form(True),
    thumbnail: UploadFile = None
):
    try:
        # Verify token
        payload = verify_token(token)
        
        # Use correct collection name
        users_collection = db.Users  # Capital U like in login.py
        
        # Debug: Check collection and find user
        print(f"Looking for teacher with ID: {teacher_id}")
        print(f"Using collection: {users_collection.name}")
        
        # Try to find any user first
        all_users = await users_collection.find({}).to_list(length=5)
        print(f"Sample users in collection: {[str(u.get('_id')) for u in all_users]}")
        
        teacher = await users_collection.find_one({"_id": ObjectId(teacher_id)})
        print(f"Found user: {teacher}")
        
        if not teacher:
            raise HTTPException(status_code=404, detail="User not found")
        
        if teacher.get("role") not in ["Teacher", "teacher"]:
            raise HTTPException(status_code=403, detail=f"User role is {teacher.get('role')}, not Teacher")
        
        # Check if token user matches teacher_id
        if payload.get("user_id") != teacher_id:
            raise HTTPException(status_code=403, detail="Unauthorized to create course for this teacher")
        
        # Upload thumbnail image
        thumbnail_url = ""
        thumbnail_public_id = ""
        if thumbnail:
            thumbnail_result = await upload_image(thumbnail, folder="course_thumbnails")
            thumbnail_url = thumbnail_result["url"]
            thumbnail_public_id = thumbnail_result["public_id"]
        
        # Create course document
        course_data = {
            "title": title,
            "description": description,
            "thumbnail_url": thumbnail_url,
            "thumbnail_public_id": thumbnail_public_id,
            "price": price,
            "teacher_id": ObjectId(teacher_id),
            "teacher_name": teacher["name"],
            "visible": visible,
            "is_active": True,
            "enrolled_count": 0,
            "videos": [],
            "created_date": datetime.utcnow(),
            "updated_date": datetime.utcnow()
        }
        
        # Insert into database
        result = await courses_collection.insert_one(course_data)
        
        return CourseResponse(
            id=str(result.inserted_id),
            title=title,
            description=description,
            thumbnail_url=thumbnail_url,
            thumbnail_public_id=thumbnail_public_id,
            price=price,
            teacher_id=teacher_id,
            teacher_name=teacher["name"],
            visible=visible,
            created_date=course_data["created_date"].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course creation failed: {str(e)}")