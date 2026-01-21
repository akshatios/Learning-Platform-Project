from datetime import datetime
from fastapi import HTTPException, UploadFile, Form
from pydantic import BaseModel
from core.database import courses_collection
from helperFunction.imageUpload import upload_image
from helperFunction.deleteAsset import delete_asset
from helperFunction.jwt_helper import verify_token
from bson import ObjectId

class CourseUpdateResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    duration: str
    thumbnail_url: str
    price: float
    visible: bool
    updated_date: str

async def update_course(
    course_id: str = Form(...),
    token: str = Form(...),
    title: str = Form(None),
    description: str = Form(None),
    category: str = Form(None),
    duration: str = Form(None),
    price: float = Form(None),
    visible: bool = Form(None),
    thumbnail: UploadFile = None
):
    try:
        # Verify token
        payload = verify_token(token)
        user_id = payload.get("user_id")
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Verify teacher owns this course or is admin
        if str(course["teacher_id"]) != user_id and payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Unauthorized to update this course")
        
        # Prepare update data
        update_data = {"updated_date": datetime.utcnow()}
        
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if category is not None:
            update_data["category"] = category
        if duration is not None:
            update_data["duration"] = duration
        if price is not None:
            update_data["price"] = price
        if visible is not None:
            update_data["visible"] = visible
        
        # Handle thumbnail update
        if thumbnail:
            # Delete old thumbnail if exists
            if course.get("thumbnail_public_id"):
                await delete_asset(course["thumbnail_public_id"])
            
            # Upload new thumbnail
            thumbnail_result = await upload_image(thumbnail, folder="course_thumbnails")
            update_data["thumbnail_url"] = thumbnail_result["url"]
            update_data["thumbnail_public_id"] = thumbnail_result["public_id"]
        
        # Update course in database
        await courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": update_data}
        )
        
        # Get updated course
        updated_course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        
        return CourseUpdateResponse(
            id=str(updated_course["_id"]),
            title=updated_course["title"],
            description=updated_course["description"],
            category=updated_course.get("category", ""),
            duration=updated_course.get("duration", ""),
            thumbnail_url=updated_course.get("thumbnail_url", ""),
            price=updated_course["price"],
            visible=updated_course.get("visible", True),
            updated_date=updated_course["updated_date"].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course update failed: {str(e)}")