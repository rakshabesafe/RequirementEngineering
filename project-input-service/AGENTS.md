# Agent Instructions for Project Input Service

## Overview

This document provides instructions for AI agents on how to programmatically interact with the `project-input-service`.

## Core Tasks

### 1. Creating a New Project

To create a new project, send a `POST` request to the service.

- **Endpoint:** `/project-api/projects/` (via the API Gateway)
- **Method:** `POST`
- **Body:**
  ```json
  {
    "name": "Your New Project Name"
  }
  ```
- **Success Response:** The service will return a JSON object representing the created project, including its unique `id`. You must store this `id` for subsequent operations.

### 2. Uploading a Document

To upload a requirements document or any other source file for a project:

1.  You must have the `project_id` from the project creation step.
2.  Construct a `multipart/form-data` request.
3.  The request must contain a `file` part with the document's content.

- **Endpoint:** `/project-api/projects/{project_id}/documents/` (replace `{project_id}` with the actual ID)
- **Method:** `POST`
- **Headers:** `'Content-Type': 'multipart/form-data'`
- **Body:** A `FormData` object containing the file.

- **Success Response:** The service will return a JSON object confirming the upload, including the `filename` and the `project_id`.

## Interaction Example (using Python with `requests`)

```python
import requests

# The API Gateway is the single entry point.
# Its default address in the docker-compose setup is http://localhost:80
GATEWAY_URL = "http://localhost"

# --- 1. Create a project ---
try:
    project_payload = {"name": "E-commerce Checkout Feature"}
    create_response = requests.post(f"{GATEWAY_URL}/project-api/projects/", json=project_payload)
    create_response.raise_for_status() # Raises an exception for bad status codes
    project_data = create_response.json()
    project_id = project_data['id']
    print(f"Project created successfully with ID: {project_id}")

    # --- 2. Upload a document to the new project ---
    file_path = "path/to/your/requirements.txt"
    # Create a dummy file for demonstration if it doesn't exist
    try:
        with open(file_path, "x") as f:
            f.write("This is a sample requirements document.")
    except FileExistsError:
        pass # File already exists

    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "text/plain")}
        upload_url = f"{GATEWAY_URL}/project-api/projects/{project_id}/documents/"
        upload_response = requests.post(upload_url, files=files)
        upload_response.raise_for_status()
        print("Document uploaded successfully:", upload_response.json())

except requests.exceptions.RequestException as e:
    print(f"An API error occurred: {e}")

```
