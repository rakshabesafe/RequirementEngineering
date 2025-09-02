# Agent Instructions for Requirements Agent Service

## Overview

This document provides instructions for AI agents on how to programmatically interact with the `requirements-agent-service`. This service uses an AI agent to turn documents into user stories in Jira.

## Core Workflow

The interaction with this service follows a two-step process:

1.  **Ingest Document**: First, you must instruct the service to process a document that has already been uploaded to MinIO. This step populates the vector database, which is necessary for the generation step. This is an asynchronous operation.
2.  **Generate Requirements**: Second, you trigger the generation process with a specific prompt. This is a synchronous operation that will return the final results.

### 1. Ingesting a Document

- **Purpose:** To load a document into the service's vector store for analysis.
- **Endpoint:** `/req-agent-api/projects/{project_id}/ingest-document`
- **Method:** `POST`
- **Body:**
  ```json
  {
    "bucket_name": "project-{project_id}",
    "object_name": "your-document-name.pdf"
  }
  ```
  - **`bucket_name`**: By convention, this should be `project-{project_id}`.
  - **`object_name`**: The name of the file in the MinIO bucket.
- **Success Response:** An `HTTP 202 Accepted` status code with a JSON body: `{"message": "Document ingestion started in the background."}`. Your agent should wait a reasonable amount of time for ingestion to complete before proceeding to the next step.

### 2. Generating Requirements

- **Purpose:** To analyze the ingested documents and create user stories in Jira.
- **Endpoint:** `/req-agent-api/projects/{project_id}/generate-requirements`
- **Method:** `POST`
- **Body:**
  ```json
  {
    "initial_prompt": "Generate user stories for the login and registration features.",
    "jira_project_key": "PROJ"
  }
  ```
- **Success Response:** An `HTTP 200 OK` with a JSON body containing the final state of the agent graph. The most important key is `jira_results`, which is a list of objects detailing each successful (or failed) push to Jira.

## Interaction Example (using Python with `requests`)

```python
import requests
import time
import json

GATEWAY_URL = "http://localhost"
PROJECT_ID = 1 # Assume project with ID 1 exists
DOC_NAME = "my_project_requirements.pdf" # Assume this was uploaded

try:
    # --- Step 1: Trigger document ingestion ---
    print("Requesting document ingestion...")
    ingest_payload = {
        "bucket_name": f"project-{PROJECT_ID}",
        "object_name": DOC_NAME
    }
    ingest_url = f"{GATEWAY_URL}/req-agent-api/projects/{PROJECT_ID}/ingest-document"
    ingest_resp = requests.post(ingest_url, json=ingest_payload)
    ingest_resp.raise_for_status()
    print(f"Ingestion started: {ingest_resp.json()['message']}")

    # In a real scenario, you might poll or use a webhook. Here, we'll just wait.
    print("Waiting for 15 seconds for ingestion to complete...")
    time.sleep(15)

    # --- Step 2: Trigger requirement generation ---
    print("Requesting requirement generation...")
    generate_payload = {
        "initial_prompt": "Generate user stories for all critical features mentioned in the document.",
        "jira_project_key": "PROJ"
    }
    generate_url = f"{GATEWAY_URL}/req-agent-api/projects/{PROJECT_ID}/generate-requirements"
    generate_resp = requests.post(generate_url, json=generate_payload)
    generate_resp.raise_for_status()

    results = generate_resp.json()
    print("--- Generation Complete ---")
    print(json.dumps(results['final_state']['jira_results'], indent=2))

except requests.exceptions.RequestException as e:
    print(f"An API error occurred: {e}")
    if e.response:
        print(f"Response Body: {e.response.text}")

```
