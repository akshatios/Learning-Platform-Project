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

async def upload_image(file: UploadFile, folder: str = "images"):
    try:
        # Check if file is image
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Upload to Cloudinary using preset
        result = cloudinary.uploader.upload(
            file.file,
            upload_preset="learning-platfrom",  # Using your preset
            folder=folder,
            resource_type="image"
        )
        
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "width": result["width"],
            "height": result["height"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

async def delete_image(public_id: str):
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image deletion failed: {str(e)}")