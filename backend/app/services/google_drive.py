import json
import io
import uuid
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = "1Msuixf3YX4bjF57SeVcOAjjSEGOmGDwP"

def get_drive_service():
    service_account_info = json.loads(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    )

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES,
    )

    return build("drive", "v3", credentials=credentials)

def upload_image_to_drive(file_bytes: bytes, content_type: str):
    service = get_drive_service()

    file_metadata = {
        "name": f"{uuid.uuid4()}",
        "parents": [FOLDER_ID],
    }

    media = MediaIoBaseUpload(
        io.BytesIO(file_bytes),
        mimetype=content_type,
        resumable=True,
    )

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
    ).execute()

    file_id = uploaded["id"]

    # Make file public
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"
