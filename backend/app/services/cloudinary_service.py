import cloudinary
import cloudinary.uploader
import os
import uuid

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True
)

def upload_image_to_cloudinary(file_bytes: bytes, content_type: str):
    result = cloudinary.uploader.upload(
        file_bytes,
        folder="community_uploads",
        public_id=str(uuid.uuid4()),
        resource_type="image"
    )

    return result["secure_url"]
