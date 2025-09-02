import logging
from minio import Minio
from minio.error import S3Error
from .config import settings

logger = logging.getLogger(__name__)

try:
    minio_client = Minio(
        settings.MINIO_URL,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False  # As we are running in Docker, not over HTTPS
    )
except Exception as e:
    logger.error(f"Failed to initialize MinIO client: {e}")
    minio_client = None

def upload_file_to_minio(bucket_name: str, file_name: str, file_data, file_size: int):
    if minio_client is None:
        raise ConnectionError("MinIO client not initialized")

    try:
        # Ensure bucket exists
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)
            logger.info(f"Bucket '{bucket_name}' created.")

        # Upload the file
        minio_client.put_object(
            bucket_name,
            file_name,
            file_data,
            file_size,
            content_type='application/octet-stream'
        )
        logger.info(f"Successfully uploaded '{file_name}' to bucket '{bucket_name}'.")

        # We can return a URL or some identifier if needed, for now just a success message
        return f"s3://{bucket_name}/{file_name}"

    except S3Error as e:
        logger.error(f"MinIO S3 Error during upload: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during file upload: {e}")
        raise
