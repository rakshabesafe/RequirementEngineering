import logging
from qdrant_client import QdrantClient, models
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List

from .config import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Manages interactions with the Qdrant vector database, including
    collection creation, document embedding, and searching.
    """
    def __init__(self):
        try:
            self.qdrant_client = QdrantClient(url=settings.QDRANT_URL)

            if settings.LLM_PROVIDER == "ollama":
                logger.info(f"Using Ollama for embeddings with model {settings.OLLAMA_MODEL_NAME}")
                self.embeddings = OllamaEmbeddings(
                    base_url=settings.OLLAMA_BASE_URL,
                    model=settings.OLLAMA_MODEL_NAME
                )
            else:
                logger.info("Using OpenAI for embeddings.")
                self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            logger.info("Qdrant client and OpenAI embeddings initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreManager: {e}")
            raise

    def get_collection_name(self, project_id: int) -> str:
        """Generates a consistent collection name for a given project."""
        return f"project_{project_id}_requirements"

    def process_and_store_documents(self, project_id: int, documents: List[Document]):
        """
        Processes raw documents, splits them into chunks, creates embeddings,
        and stores them in a project-specific Qdrant collection.
        """
        collection_name = self.get_collection_name(project_id)

        logger.info(f"Processing {len(documents)} document(s) for project {project_id} into collection '{collection_name}'.")

        # Split documents into smaller chunks
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split documents into {len(chunks)} chunks.")

        # Check if the collection already exists, if not, create it
        try:
            self.qdrant_client.get_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' already exists.")
        except Exception:
            logger.info(f"Collection '{collection_name}' not found. Creating new collection.")
            # Dynamically determine vector size from the embedding model
            test_vector = self.embeddings.embed_query("test")
            vector_size = len(test_vector)
            logger.info(f"Detected vector size of {vector_size} from the embedding model.")

            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )

        # Embed the chunks and upsert them into Qdrant
        # Note: qdrant_client.add can handle the embedding process internally
        # if we use langchain's Qdrant wrapper, but doing it explicitly gives more control.

        texts_to_embed = [chunk.page_content for chunk in chunks]
        vectors = self.embeddings.embed_documents(texts_to_embed)

        # Add the original text content to the payload
        payloads = [chunk.metadata for chunk in chunks]
        for i, text in enumerate(texts_to_embed):
            payloads[i]['page_content'] = text

        self.qdrant_client.upsert(
            collection_name=collection_name,
            points=models.Batch(
                ids=None, # Let Qdrant assign IDs
                vectors=vectors,
                payloads=payloads
            ),
            wait=True
        )
        logger.info(f"Successfully upserted {len(chunks)} chunks into '{collection_name}'.")

    def search(self, project_id: int, query: str, limit: int = 5) -> List[Document]:
        """
        Performs a similarity search in the specified project's collection.
        """
        collection_name = self.get_collection_name(project_id)
        query_vector = self.embeddings.embed_query(query)

        logger.info(f"Searching in collection '{collection_name}' with query: '{query}'")

        hits = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )

        # Convert search hits back to LangChain Document objects
        results = [
            Document(
                page_content=hit.payload.get('page_content', ''),
                metadata={k: v for k, v in hit.payload.items() if k != 'page_content'}
            )
            for hit in hits
        ]
        logger.info(f"Found {len(results)} relevant documents.")
        return results

# Singleton instance
vector_store_manager = VectorStoreManager()
