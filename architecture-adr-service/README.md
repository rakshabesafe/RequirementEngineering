# Architecture ADR Service

## Purpose

This service is the source of truth for all architectural models and Architecture Decision Records (ADRs). It is designed around the principle of immutability: architectural models are never updated in place. Instead, any change results in a new, versioned entry.

## Core Technologies

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (using `JSONB` for flexible, indexable storage of models)

## API Endpoints

All endpoints are accessible through the API Gateway (Kong) under the `/arch-api` prefix.

### Architecture Families

- **`POST /architectures/`**: Creates a new "family" or container for an architectural design.
  - **Request Body:**
    ```json
    {
      "project_id": integer,
      "name": "string"
    }
    ```

- **`GET /architectures/{arch_id}`**: Retrieves details for an architecture family, including its latest version.

### Version Management

- **`POST /architectures/{arch_id}/versions/`**: Creates a new, immutable version of an architecture. The version number is incremented automatically by the service.
  - **Request Body:**
    ```json
    {
      "model_data": {
        "key": "value",
        "diagram": "PlantUML or MermaidJS syntax here"
      }
    }
    ```

- **`GET /architectures/{arch_id}/versions/`**: Lists all versions for an architecture, newest first.

- **`GET /architectures/{arch_id}/versions/latest`**: Retrieves the most recent version of an architecture.

- **`GET /architectures/{arch_id}/versions/{version_num}`**: Retrieves a specific version of an architecture.

## Running the Service

The service is containerized and managed by the main `docker-compose.yml` file. It depends on the PostgreSQL service.

To run this service as part of the entire platform:
```bash
sudo docker compose up --build
```
