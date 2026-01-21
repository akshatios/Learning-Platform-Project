import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

async def delete_asset(public_id: str, resource_type: str = "image"):
    """
    Delete asset from Cloudinary
    resource_type: 'image', 'video', 'raw'
    """
    try:
        print(f"Attempting to delete: '{public_id}' of type: {resource_type}")
        
        result = cloudinary.uploader.destroy(
            public_id, 
            resource_type=resource_type
        )
        
        print(f"Delete result: {result}")
        
        if result.get("result") == "ok":
            return {"success": True, "message": f"{resource_type.capitalize()} deleted successfully", "public_id": public_id}
        elif result.get("result") == "not found":
            return {"success": False, "message": f"{resource_type.capitalize()} not found", "public_id": public_id}
        else:
            return {"success": False, "message": f"Failed to delete {resource_type}", "result": result}
            
    except Exception as e:
        print(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

async def delete_multiple_assets(public_ids: list, resource_type: str = "image"):
    """
    Delete multiple assets from Cloudinary
    """
    try:
        result = cloudinary.api.delete_resources(
            public_ids,
            resource_type=resource_type
        )
        
        return {
            "success": True,
            "deleted": result.get("deleted", {}),
            "not_found": result.get("not_found", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk deletion failed: {str(e)}")

async def delete_folder(folder_path: str):
    """
    Delete entire folder from Cloudinary
    """
    try:
        result = cloudinary.api.delete_folder(folder_path)
        return {"success": True, "message": f"Folder '{folder_path}' deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Folder deletion failed: {str(e)}")