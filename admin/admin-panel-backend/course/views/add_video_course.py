from datetime import datetime
from fastapi import HTTPException, UploadFile, Form
from pydantic import BaseModel
from core.database import courses_collection, course_videos_collection
from helperFunction.videoUpload import upload_video
from helperFunction.jwt_helper import verify_token
from bson import ObjectId

class VideoResponse(BaseModel):
    id: str
    course_id: str
    title: str
    description: str
    video_url: str
    video_public_id: str
    created_date: str

async def add_video_to_course(
    token: str = Form(...),
    course_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    video_file: UploadFile = None
):
    try:
        # Verify token
        verify_token(token)
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Upload video
        video_url = ""
        video_public_id = ""
        if video_file:
            video_result = await upload_video(video_file, folder="course_videos")
            video_url = video_result["url"]
            video_public_id = video_result["public_id"]
        
        # Create video document
        video_data = {
            "course_id": ObjectId(course_id),
            "title": title,
            "description": description,
            "video_url": video_url,
            "video_public_id": video_public_id,
            "created_date": datetime.utcnow()
        }
        
        # Insert video into course_videos collection
        video_result = await course_videos_collection.insert_one(video_data)
        video_object_id = video_result.inserted_id
        
        # Add video ObjectId to course's videos array
        await courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$push": {"videos": video_object_id}}
        )
        
        return VideoResponse(
            id=str(video_object_id),
            course_id=course_id,
            title=title,
            description=description,
            video_url=video_url,
            video_public_id=video_public_id,
            created_date=video_data["created_date"].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video addition failed: {str(e)}")