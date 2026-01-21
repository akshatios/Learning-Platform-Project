from fastapi import HTTPException, Query
from typing import List, Optional
from core.database import courses_collection, users_collection
from helperFunction.jwt_helper import verify_token
from bson import ObjectId

async def get_courses():
    try:
        print("Starting get_courses function")
        # Get all courses from database
        courses_cursor = courses_collection.find({})
        courses = await courses_cursor.to_list(length=None)
        print(f"Found {len(courses)} courses")
        
        course_list = []
        for course in courses:
            try:
                course_data = {
                    "_id": str(course["_id"]),
                    "title": course.get("title", ""),
                    "description": course.get("description", ""),
                    "thumbnail_url": course.get("thumbnail_url", ""),
                    "thumbnail_public_id": course.get("thumbnail_public_id", ""),
                    "price": course.get("price", 0),
                    "visible": course.get("visible", True),
                    "created_date": str(course.get("created_date", "")),
                    "videos": [str(video_id) for video_id in course.get("videos", [])],
                    "updated_date": str(course.get("updated_date", "")),
                    "enrolled_count": course.get("enrolled_count", 0)
                }
                course_list.append(course_data)
            except Exception as course_error:
                print(f"Error processing course {course.get('_id')}: {course_error}")
                continue
        
        result = {"courses": course_list, "total": len(course_list)}
        print(f"Returning result: {result}")
        return result
        
    except Exception as e:
        print(f"Error in get_courses: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch courses: {str(e)}")

async def get_teacher_courses(teacher_id: str, token: str = Query(...)):
    try:
        # Verify token
        payload = verify_token(token)
        
        # Check if token user matches teacher_id or is admin
        if payload.get("user_id") != teacher_id and payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Unauthorized to view these courses")
        
        # Get teacher's courses
        courses_cursor = courses_collection.find({"teacher_id": ObjectId(teacher_id)}).sort("created_date", -1)
        courses = await courses_cursor.to_list(length=None)
        
        course_list = []
        for course in courses:
            course_data = {
                "id": str(course["_id"]),
                "title": course["title"],
                "description": course["description"],
                "category": course.get("category", ""),
                "duration": course.get("duration", ""),
                "thumbnail_url": course.get("thumbnail_url", ""),
                "price": course["price"],
                "teacher_name": course.get("teacher_name", ""),
                "enrolled_count": course.get("enrolled_count", 0),
                "visible": course.get("visible", True),
                "created_date": course["created_date"].isoformat() if course.get("created_date") else ""
            }
            course_list.append(course_data)
        
        return {"courses": course_list, "total": len(course_list)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch teacher courses: {str(e)}")

async def search_courses(query: str, category: str = Query(None)):
    try:
        search_filter = {
            "visible": True,
            "is_active": True,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"teacher_name": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if category:
            search_filter["category"] = category
        
        courses_cursor = courses_collection.find(search_filter).sort("created_date", -1)
        courses = await courses_cursor.to_list(length=None)
        
        course_list = []
        for course in courses:
            course_data = {
                "id": str(course["_id"]),
                "title": course["title"],
                "description": course["description"],
                "category": course.get("category", ""),
                "duration": course.get("duration", ""),
                "thumbnail_url": course.get("thumbnail_url", ""),
                "price": course["price"],
                "teacher_name": course.get("teacher_name", ""),
                "enrolled_count": course.get("enrolled_count", 0),
                "visible": course.get("visible", True),
                "created_date": course["created_date"].isoformat() if course.get("created_date") else ""
            }
            course_list.append(course_data)
        
        return {"courses": course_list, "total": len(course_list)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")