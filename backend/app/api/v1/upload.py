from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.google_drive import upload_image_to_drive

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

@router.post("/photo")
async def upload_photo(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed"
        )

    file_bytes = await file.read()

    photo_url = upload_image_to_drive(
        file_bytes,
        file.content_type
    )

    return {
        "photo_url": photo_url
    }
