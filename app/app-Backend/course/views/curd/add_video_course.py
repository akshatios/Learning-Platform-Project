from datetime import datetime
from fastapi import HTTPException, UploadFile, Form, Query
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
        payload = verify_token(token)
        
        # Validate course_id
        if not course_id or course_id == 'undefined':
            raise HTTPException(status_code=400, detail="Invalid course ID")
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if user is teacher of this course
        if str(course.get("teacher_id")) != payload.get("user_id"):
            raise HTTPException(status_code=403, detail="Only course teacher can add videos")
        
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

async def get_course_videos(course_id: str, token: str = Query(...)):
    try:
        # Verify token
        verify_token(token)
        
        # Get videos for course
        videos_cursor = course_videos_collection.find({"course_id": ObjectId(course_id)})
        videos = await videos_cursor.to_list(length=None)
        
        video_list = []
        for video in videos:
            video_data = {
                "id": str(video["_id"]),
                "course_id": str(video["course_id"]),
                "title": video["title"],
                "description": video["description"],
                "video_url": video["video_url"],
                "created_date": video["created_date"].isoformat()
            }
            video_list.append(video_data)
        
        return {"videos": video_list, "total": len(video_list)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")