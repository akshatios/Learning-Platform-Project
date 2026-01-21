from fastapi import HTTPException, Query
from pydantic import BaseModel
from core.database import courses_collection, course_videos_collection
from helperFunction.jwt_helper import verify_token
from typing import List
from bson import ObjectId

class VideoInfo(BaseModel):
    id: str
    title: str
    video_url: str

class CourseListResponse(BaseModel):
    id: str
    title: str
    description: str
    thumbnail_url: str
    thumbnail_public_id: str
    price: float
    visible: bool
    created_date: str
    videos: List[VideoInfo]

async def get_courses(token: str = Query(...)):
    try:
        # Verify token
        verify_token(token)
        
        courses = []
        async for course in courses_collection.find():
            # Get videos for this course
            videos = []
            if course.get("videos"):
                for video_id in course["videos"]:
                    video = await course_videos_collection.find_one({"_id": ObjectId(video_id)})
                    if video:
                        videos.append(VideoInfo(
                            id=str(video["_id"]),
                            title=video["title"],
                            video_url=video["video_url"]
                        ))
            
            courses.append(CourseListResponse(
                id=str(course["_id"]),
                title=course["title"],
                description=course["description"],
                thumbnail_url=course.get("thumbnail_url", ""),
                thumbnail_public_id=course.get("thumbnail_public_id", ""),
                price=course["price"],
                visible=course["visible"],
                created_date=course["created_date"].isoformat(),
                videos=videos
            ))
        
        return {
            "success": True, 
            "total_courses": len(courses),
            "courses": courses
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch courses: {str(e)}")