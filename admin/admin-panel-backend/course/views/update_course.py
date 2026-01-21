from datetime import datetime
from fastapi import HTTPException, UploadFile, Form
from pydantic import BaseModel
from core.database import courses_collection
from helperFunction.imageUpload import upload_image
from helperFunction.deleteAsset import delete_asset
from helperFunction.jwt_helper import verify_token
from bson import ObjectId

class UpdateCourseResponse(BaseModel):
    id: str
    title: str
    description: str
    thumbnail_url: str
    thumbnail_public_id: str
    price: float
    visible: bool
    updated_date: str

async def update_course(
    token: str = Form(...),
    course_id: str = Form(...),
    title: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    visible: bool = Form(None),
    thumbnail: UploadFile = None
):
    try:
        # Verify token
        verify_token(token)
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Prepare update data
        update_data = {"updated_date": datetime.utcnow()}
        
        # Update fields if provided
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if price is not None:
            update_data["price"] = price
        if visible is not None:
            update_data["visible"] = visible
        
        # Handle thumbnail update
        if thumbnail:
            # Delete old thumbnail from cloud
            if course.get("thumbnail_public_id"):
                try:
                    await delete_asset(course["thumbnail_public_id"], "image")
                except:
                    pass  # Continue even if old thumbnail deletion fails
            
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
        
        return UpdateCourseResponse(
            id=str(updated_course["_id"]),
            title=updated_course["title"],
            description=updated_course["description"],
            thumbnail_url=updated_course.get("thumbnail_url", ""),
            thumbnail_public_id=updated_course.get("thumbnail_public_id", ""),
            price=updated_course["price"],
            visible=updated_course["visible"],
            updated_date=updated_course["updated_date"].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course update failed: {str(e)}")