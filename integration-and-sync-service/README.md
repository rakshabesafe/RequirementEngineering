# Integration and Sync Service

## Purpose

This service acts as a centralized hub for all communication with external, third-party tools. It is designed with a pluggable adapter framework to make it easy to add new integrations in the future.

The initial implementation provides a one-way integration to **Jira**, allowing other services to create issues programmatically.

## Core Technologies

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (for mapping internal artifact IDs to external tool IDs)
- **Jira Client:** `atlassian-python-api`

## Configuration

This service requires credentials for the external tools it integrates with. These must be provided as environment variables in the `docker-compose.yml` file.

**Required for Jira:**
```yaml
environment:
  - JIRA_URL=https://your-jira-instance.atlassian.net
  - JIRA_USERNAME=your-email@example.com
  - JIRA_API_TOKEN=your-api-token
```

## API Endpoints

All endpoints are accessible through the API Gateway (Kong) under the `/integration-api` prefix.

### Jira Integration

- **`POST /integrations/jira/issues`**: Creates a new issue in Jira.
  - **Request Body:**
    ```json
    {
      "internal_id": "string (unique ID from the source service)",
      "source_service": "string (e.g., 'requirements-agent-service')",
      "project_key": "string (e.g., 'PROJ')",
      "title": "string",
      "description": "string",
      "issue_type": "string (e.g., 'Task', 'Story')"
    }
    ```
  - **Success Response:** Returns a detailed object including the created Jira issue's key, ID, URL, and the internal mapping record.

## Running the Service

The service is containerized and managed by the main `docker-compose.yml` file. It depends on the PostgreSQL service.

To run this service as part of the entire platform:
```bash
sudo docker compose up --build
```
**Note:** Ensure the Jira environment variables are correctly set before running.
