import logging
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class R2StorageService:
    def __init__(self):
        self.bucket_name = settings.R2_BUCKET_NAME
        # Initialize client if config exists
        if settings.R2_ACCOUNT_ID and settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY:
            r2_endpoint = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
            self.s3_client = boto3.client(
                's3',
                endpoint_url=r2_endpoint,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                region_name='auto'  # R2 uses auto
            )
            self.configured = True
        else:
            self.s3_client = None
            self.configured = False
            logger.warning("R2 Storage is not configured.")

    async def upload_resume(self, file: UploadFile, student_id: str) -> str:
        """Uploads a resume PDF to R2 and returns the file key."""
        if not self.configured:
            logger.warning("R2 not configured, skipping actual upload. Returning mock path.")
            return f"resumes/{student_id}/{file.filename}"
            
        file_key = f"resumes/{student_id}/{file.filename}"
        
        try:
            content = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=content,
                ContentType=file.content_type
            )
            await file.seek(0)
            return file_key
        except ClientError as e:
            logger.error(f"Failed to upload {file.filename} to R2: {e}")
            raise Exception(f"Storage upload failed: {e}")

r2_storage = R2StorageService()
