from datetime import datetime
from fastapi import HTTPException, UploadFile, Form
from pydantic import BaseModel
from core.database import courses_collection
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
    visible: bool
    created_date: str

async def create_course(
    token: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    visible: bool = Form(True),
    thumbnail: UploadFile = None
):
    try:
        # Verify token
        verify_token(token)
        
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
            "visible": visible,
            "created_date": datetime.utcnow()
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
            visible=visible,
            created_date=course_data["created_date"].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course creation failed: {str(e)}")