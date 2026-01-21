from fastapi import HTTPException, Query
from core.database import courses_collection, course_videos_collection
from helperFunction.jwt_helper import verify_token
from helperFunction.deleteAsset import delete_asset
from bson import ObjectId

async def delete_course(course_id: str = Query(...), token: str = Query(...)):
    try:
        # Verify token
        verify_token(token)
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Delete course thumbnail from cloud
        if course.get("thumbnail_public_id"):
            try:
                await delete_asset(course["thumbnail_public_id"], "image")
            except:
                pass  # Continue even if cloud deletion fails
        
        # Get all videos for this course
        videos = []
        async for video in course_videos_collection.find({"course_id": ObjectId(course_id)}):
            videos.append(video)
        
        # Delete all videos from cloud
        for video in videos:
            if video.get("video_public_id"):
                try:
                    await delete_asset(video["video_public_id"], "video")
                except:
                    pass  # Continue even if cloud deletion fails
        
        # Delete all videos from course_videos collection
        await course_videos_collection.delete_many({"course_id": ObjectId(course_id)})
        
        # Delete course from courses collection
        await courses_collection.delete_one({"_id": ObjectId(course_id)})
        
        return {
            "success": True, 
            "message": "Course and all associated content deleted successfully",
            "deleted_videos": len(videos)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course deletion failed: {str(e)}")