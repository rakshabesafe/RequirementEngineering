import logging
from minio import Minio
from minio.error import S3Error
from .config import settings
import os

logger = logging.getLogger(__name__)

try:
    minio_client = Minio(
        settings.MINIO_URL,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )
except Exception as e:
    logger.error(f"Failed to initialize MinIO client: {e}")
    minio_client = None

def download_document(bucket_name: str, object_name: str) -> str | None:
    """
    Downloads a document from MinIO and saves it to a temporary local file.

    :param bucket_name: The MinIO bucket where the document is stored.
    :param object_name: The name of the document object in the bucket.
    :return: The local path to the downloaded file, or None if download fails.
    """
    if not minio_client:
        logger.error("MinIO client not initialized.")
        return None

    try:
        # Create a temporary directory to store the downloaded file
        temp_dir = "/tmp/documents"
        os.makedirs(temp_dir, exist_ok=True)
        local_file_path = os.path.join(temp_dir, object_name)

        logger.info(f"Downloading {object_name} from bucket {bucket_name} to {local_file_path}...")

        minio_client.fget_object(bucket_name, object_name, local_file_path)

        logger.info(f"Successfully downloaded document to {local_file_path}.")
        return local_file_path

    except S3Error as e:
        logger.error(f"MinIO S3 Error during download: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during document download: {e}")
        return None
