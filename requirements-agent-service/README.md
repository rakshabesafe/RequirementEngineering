# Requirements Agent Service

## Purpose

This service is a core component of the AI Agent Cortex. It hosts an AI agent, built with LangGraph, that is responsible for analyzing project documents, generating user stories, and pushing them to an external tracker (Jira) via the `integration-and-sync-service`.

## Core Technologies

- **Backend:** FastAPI (Python)
- **AI Framework:** LangChain & LangGraph
- **LLM Support:** OpenAI, Ollama (configurable)
- **Vector Database:** Qdrant (for RAG)
- **Document Parsing:** Unstructured.io

## Configuration

This service has several important configuration options that must be set as environment variables in the `docker-compose.yml` file.

- **`LLM_PROVIDER`**: Determines which language model to use. Can be `openai` (default) or `ollama`.

- **If `LLM_PROVIDER=openai`:**
  - `OPENAI_API_KEY`: Your secret API key from OpenAI.

- **If `LLM_PROVIDER=ollama`:**
  - `OLLAMA_BASE_URL`: The URL of your running Ollama instance (e.g., `http://host.docker.internal:11434` to connect to Ollama on the host machine).
  - `OLLAMA_MODEL_NAME`: The name of the Ollama model to use (e.g., `llama3`).

## API Endpoints

All endpoints are accessible through the API Gateway (Kong) under the `/req-agent-api` prefix.

- **`POST /projects/{project_id}/ingest-document`**: Triggers the asynchronous ingestion of a document. The service downloads the specified document from MinIO, processes it with `unstructured`, and stores its vector embeddings in the project-specific Qdrant collection. This must be called before generating requirements.
  - **Request Body:**
    ```json
    {
      "bucket_name": "string (e.g., 'project-1')",
      "object_name": "string (e.g., 'requirements.pdf')"
    }
    ```

- **`POST /projects/{project_id}/generate-requirements`**: Starts the main agentic workflow. It uses the previously ingested documents to generate user stories and push them to Jira.
  - **Request Body:**
    ```json
    {
      "initial_prompt": "string (e.g., 'Generate user stories for the key features.')",
      "jira_project_key": "string (e.g., 'PROJ')"
    }
    ```
  - **Success Response:** Returns the final state of the LangGraph agent, including the results of the Jira push operations.

## Running the Service

The service is containerized and managed by the main `docker-compose.yml` file. It depends on Qdrant, MinIO, and the `integration-and-sync-service`.

To run this service as part of the entire platform:
```bash
sudo docker compose up --build
```
**Note:** Ensure the LLM provider and API keys are correctly set before running.
