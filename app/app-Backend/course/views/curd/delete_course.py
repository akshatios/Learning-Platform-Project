from fastapi import HTTPException, Form
from pydantic import BaseModel
from core.database import courses_collection, course_videos_collection
from helperFunction.deleteAsset import delete_asset
from helperFunction.jwt_helper import verify_token
from bson import ObjectId

class DeleteResponse(BaseModel):
    message: str
    deleted_course_id: str

async def delete_course(
    course_id: str = Form(...),
    token: str = Form(...)
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
            raise HTTPException(status_code=403, detail="Unauthorized to delete this course")
        
        # Delete course thumbnail from cloudinary if exists
        if course.get("thumbnail_public_id"):
            await delete_asset(course["thumbnail_public_id"])
        
        # Get all videos for this course
        videos = await course_videos_collection.find({"course_id": ObjectId(course_id)}).to_list(length=None)
        
        # Delete all video files from cloudinary
        for video in videos:
            if video.get("video_public_id"):
                await delete_asset(video["video_public_id"])
        
        # Delete all videos from course_videos collection
        await course_videos_collection.delete_many({"course_id": ObjectId(course_id)})
        
        # Delete course from courses collection
        await courses_collection.delete_one({"_id": ObjectId(course_id)})
        
        return DeleteResponse(
            message="Course and all associated videos deleted successfully",
            deleted_course_id=course_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course deletion failed: {str(e)}")