from supabase import create_client, Client
from fastapi import UploadFile, HTTPException
import uuid , mimetypes
from app.config import settings 
import httpx

SUPABASE_URL = settings.supabase_url
SUPABASE_SERVICE_ROLE_KEY = settings.supabase_service_role_key
BUCKET = settings.supabase_bucket

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def upload_to_supabase(file, folder: str):
    """
    Upload file to Supabase Storage and return public URL.
    """
    # Get extension
    ext = file.filename.split(".")[-1]

    # Generate unique name
    file_name = f"{uuid.uuid4()}.{ext}"

    # Full path in bucket
    file_path = f"{folder}/{file_name}"

    # Read file bytes from UploadFile
    file_bytes = file.file.read()

   
    # Upload (IMPORTANT: use file_bytes, NOT file.file)
    supabase.storage.from_(BUCKET).upload(
        path=file_path,
        file=file_bytes,  # MUST be bytes
        file_options={"content-type": file.content_type}
    )

    # Return public URL
    public_url = supabase.storage.from_(BUCKET).get_public_url(file_path)

    return public_url


# async def upload_to_supabase(file: UploadFile, folder: str) -> str:
#     ext = file.filename.split(".")[-1]
#     file_name = f"{uuid.uuid4()}.{ext}"
#     file_path = f"{folder}/{file_name}"

#     file_bytes = await file.read()

#     url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{file_path}"

#     headers = {
#         "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
#         "Content-Type": file.content_type or "application/octet-stream",
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, content=file_bytes, headers=headers)

#     # Print everything for debugging
#     print("Status:", response.status_code)
#     print("Body:", response.text)

#     if response.status_code not in (200, 201):
#         raise HTTPException(
#             status_code=500,
#             detail=f"Supabase upload failed: {response.status_code} - {response.text}"
#         )

#     public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{file_path}"
#     return public_url

def upload_to_supabase_qr(file_path: str, folder: str) -> str:
    """
    Upload local file (QR image) to Supabase
    """
    ext = file_path.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{ext}"
    storage_path = f"{folder}/{file_name}"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    content_type = mimetypes.guess_type(file_path)[0] or "image/png"

    supabase.storage.from_(BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": content_type}
    )

    return supabase.storage.from_(BUCKET).get_public_url(storage_path)