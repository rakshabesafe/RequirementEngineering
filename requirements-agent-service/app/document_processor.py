import logging
from unstructured.loader import UnstructuredFileLoader
from typing import List

from .minio_client import download_document
from .vector_store import vector_store_manager

logger = logging.getLogger(__name__)

def process_document_for_project(project_id: int, bucket_name: str, object_name: str) -> bool:
    """
    Orchestrates the process of downloading a document, processing it,
    and storing it in the vector database for a specific project.

    :param project_id: The ID of the project.
    :param bucket_name: The MinIO bucket where the document resides.
    :param object_name: The name of the document object in the bucket.
    :return: True if processing was successful, False otherwise.
    """
    logger.info(f"Starting document processing for project {project_id}, bucket '{bucket_name}', object '{object_name}'.")

    # 1. Download the document from MinIO to a local temp file
    local_file_path = download_document(bucket_name, object_name)
    if not local_file_path:
        logger.error("Failed to download document. Aborting processing.")
        return False

    # 2. Load the document using UnstructuredFileLoader
    # This automatically handles various file types (PDF, DOCX, etc.)
    try:
        logger.info(f"Loading document from local path: {local_file_path}")
        loader = UnstructuredFileLoader(local_file_path)
        documents = loader.load()

        # Add the source document name to the metadata of each loaded document part
        for doc in documents:
            doc.metadata['source'] = object_name

    except Exception as e:
        logger.error(f"Failed to load document with Unstructured: {e}")
        return False

    if not documents:
        logger.warning("Document loaded but resulted in no content.")
        return True # Not a failure, but nothing to process

    # 3. Use the VectorStoreManager to process and store the document chunks
    try:
        vector_store_manager.process_and_store_documents(project_id, documents)
        logger.info("Successfully processed and stored document in vector store.")
        return True
    except Exception as e:
        logger.error(f"Failed to process and store document in vector store: {e}")
        return False

    # Note: In a production system, you might want to clean up the temp file.
    # For this project, we can leave it, as the container is ephemeral.
