import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

async def upload_video(file: UploadFile, folder: str = "videos"):
    try:
        # Check if file is video
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Upload to Cloudinary using preset
        result = cloudinary.uploader.upload(
            file.file,
            upload_preset="learning-platfrom",  # Using your preset
            folder=folder,
            resource_type="video"
        )
        
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "duration": result.get("duration"),
            "width": result.get("width"),
            "height": result.get("height")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video upload failed: {str(e)}")

async def delete_video(public_id: str):
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="video")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video deletion failed: {str(e)}")