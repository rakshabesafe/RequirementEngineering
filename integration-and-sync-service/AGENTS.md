# Agent Instructions for Integration and Sync Service

## Overview

This document provides instructions for AI agents on how to programmatically use the `integration-and-sync-service` to push artifacts to external tools like Jira.

## Core Tasks

### 1. Creating a Jira Issue

This is the primary function for Phase 1. To create a Jira issue, you need to provide all the necessary details for the ticket.

- **Endpoint:** `/integration-api/integrations/jira/issues` (via the API Gateway)
- **Method:** `POST`
- **Body:** The request body must conform to the `JiraIssueCreateRequest` schema.
  ```json
  {
    "internal_id": "unique-id-from-your-service-e.g.,-uuid",
    "source_service": "name-of-the-calling-service",
    "project_key": "JIRA_PROJECT_KEY",
    "title": "This is the issue title",
    "description": "This is the main body of the issue. It can contain markdown.",
    "issue_type": "Story"
  }
  ```
  - **`internal_id`**: This must be a unique identifier for the artifact you are pushing. This is crucial for future traceability. A UUID is a good choice.
  - **`source_service`**: The name of your agent or service.
  - **`issue_type`**: Must be a valid issue type in the target Jira project (e.g., 'Task', 'Story', 'Bug', 'Epic').

- **Success Response:** The service returns a JSON object containing the `jira_key`, `jira_id`, `jira_url`, and the created database `mapping`.

## Important Considerations

- **Idempotency Check:** This service checks if an `internal_id` has already been synced to Jira. If it has, the service will return an `HTTP 409 Conflict` error and will not create a duplicate issue. Your agent should be prepared to handle this response.
- **Authentication:** Your agent does not need to handle Jira authentication directly. This service is pre-configured with the necessary credentials via environment variables.

## Interaction Example (using Python with `requests`)

```python
import requests
import uuid

GATEWAY_URL = "http://localhost"

# This example assumes the 'requirements-agent-service' is calling this service.
try:
    # 1. Prepare the payload for a new Jira issue
    story_title = "Implement user login via email"
    story_description = "As a user, I want to log in with my email and password so that I can access my account."

    payload = {
        "internal_id": f"story-{uuid.uuid4()}",
        "source_service": "requirements-agent-service",
        "project_key": "PROJ", # The target Jira project key
        "title": story_title,
        "description": story_description,
        "issue_type": "Story"
    }

    # 2. Send the request to the integration service
    response = requests.post(f"{GATEWAY_URL}/integration-api/integrations/jira/issues", json=payload)
    response.raise_for_status() # Will raise an exception for 4xx or 5xx status codes

    # 3. Process the successful response
    data = response.json()
    print(f"Successfully created Jira issue: {data['jira_key']}")
    print(f"Jira URL: {data['jira_url']}")
    print(f"DB Mapping ID: {data['mapping']['id']}")

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 409:
        print(f"Conflict: This artifact has likely already been synced. Details: {e.response.text}")
    else:
        print(f"An HTTP error occurred: {e.response.status_code} {e.response.text}")
except requests.exceptions.RequestException as e:
    print(f"A network error occurred: {e}")

```
