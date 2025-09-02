# Project Input Service

## Purpose

This service is responsible for managing projects and ingesting user documents within the AI SDLC Platform. It provides the foundational entities (projects) to which all other artifacts are linked.

## Core Technologies

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (for project metadata)
- **Storage:** MinIO (for uploaded source documents)

## API Endpoints

All endpoints are accessible through the API Gateway (Kong) under the `/project-api` prefix.

### Project Management

- **`POST /projects/`**: Creates a new project.
  - **Request Body:**
    ```json
    {
      "name": "string"
    }
    ```
  - **Response:**
    ```json
    {
      "name": "string",
      "id": integer,
      "created_at": "datetime"
    }
    ```

- **`GET /projects/`**: Retrieves a list of all projects.

- **`GET /projects/{project_id}`**: Retrieves a single project by its ID.

### Document Management

- **`POST /projects/{project_id}/documents/`**: Uploads a document to a specific project.
  - **Request Body:** `multipart/form-data` with a `file` field containing the document.
  - **Behavior:** The document is stored in a MinIO bucket named `project-{project_id}`.

## Running the Service

The service is containerized and managed by the main `docker-compose.yml` file at the root of the project. It depends on the PostgreSQL and MinIO services.

To run this service as part of the entire platform:
```bash
sudo docker compose up --build
```
