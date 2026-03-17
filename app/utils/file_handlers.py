import os
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import List

ALLOWED_IMAGE_EXTENSIONS = ['.dcm', '.nii', '.nii.gz', '.mhd', '.nrrd', '.vtk', '.stl', '.obj']

async def save_uploaded_file(upload_file: UploadFile, destination: str) -> str:
    """Save uploaded file to destination"""
    try:
        # Validate file extension
        file_extension = os.path.splitext(upload_file.filename)[1].lower()
        if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not allowed. Allowed: {ALLOWED_IMAGE_EXTENSIONS}"
            )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Save file
        async with aiofiles.open(destination, 'wb') as buffer:
            content = await upload_file.read()
            await buffer.write(content)
        
        return destination
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def validate_file_size(file_path: str, max_size: int = 500 * 1024 * 1024) -> bool:
    """Validate file size"""
    return get_file_size(file_path) <= max_size

def cleanup_old_files(directory: str, max_files: int = 10):
    """Cleanup old files keeping only the most recent ones"""
    try:
        if not os.path.exists(directory):
            return
            
        files = [os.path.join(directory, f) for f in os.listdir(directory)]
        files = [f for f in files if os.path.isfile(f)]
        
        # Sort by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)
        
        # Remove old files
        for file_path in files[max_files:]:
            os.remove(file_path)
            
    except Exception as e:
        print(f"Error cleaning up files: {e}")
        