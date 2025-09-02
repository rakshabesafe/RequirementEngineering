from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Qdrant Configuration
    QDRANT_URL: str = "http://qdrant:6333"

    # MinIO Configuration
    MINIO_URL: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "openai"  # Can be 'openai' or 'ollama'

    # OpenAI Configuration
    # IMPORTANT: This must be set in the environment if LLM_PROVIDER is 'openai'.
    OPENAI_API_KEY: str = "your-openai-api-key"
    OPENAI_MODEL_NAME: str = "gpt-4-turbo"

    # Ollama Configuration
    # Assumes Ollama is running on the host machine.
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    OLLAMA_MODEL_NAME: str = "llama3"

    # Internal Service URLs
    INTEGRATION_SERVICE_URL: str = "http://integration-and-sync-service:8000"

    # Default Jira project key (can be overridden in API calls)
    DEFAULT_JIRA_PROJECT_KEY: Optional[str] = "PROJ"

    class Config:
        # Allows populating settings from environment variables
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
