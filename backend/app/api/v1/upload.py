from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.cloudinary_service import upload_image_to_cloudinary


router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

@router.post("/photo")
async def upload_photo(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Only JPG and PNG allowed")

    file_bytes = await file.read()

    photo_url = upload_image_to_cloudinary(
        file_bytes,
        file.content_type
    )

    return {"photo_url": photo_url}

