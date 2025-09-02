# Agent Instructions for Architecture ADR Service

## Overview

This document provides instructions for AI agents on how to programmatically interact with the `architecture-adr-service`. This service manages versioned architectural models.

## Core Concepts

- **Architecture Family**: A container for a specific architectural component (e.g., "User Authentication System"). It is identified by a unique `arch_id`.
- **Architecture Version**: An immutable snapshot of the architectural design for a family. Each version has a unique, auto-incrementing `version` number.

## Core Tasks

### 1. Creating an Architecture Family

Before creating versions, you must first create a family to hold them.

- **Endpoint:** `/arch-api/architectures/` (via the API Gateway)
- **Method:** `POST`
- **Body:**
  ```json
  {
    "project_id": 1,
    "name": "User Authentication System"
  }
  ```
- **Success Response:** The service will return a JSON object for the created family, including its `id`. Store this `arch_id` for future use.

### 2. Creating a New Architecture Version

Once you have an `arch_id`, you can create a new version of the architecture.

- **Endpoint:** `/arch-api/architectures/{arch_id}/versions/`
- **Method:** `POST`
- **Body:** The `model_data` can be any valid JSON object.
  ```json
  {
    "model_data": {
      "type": "C4Model",
      "scope": "System",
      "components": [
        {"name": "Frontend", "technology": "React"},
        {"name": "Backend API", "technology": "FastAPI"}
      ],
      "diagram": "plantuml\n@startuml\n...diagram syntax...\n@enduml"
    }
  }
  ```
- **Success Response:** Returns the full version object, including the new `version` number.

### 3. Retrieving the Latest Version

To get the most recent version of an architecture:

- **Endpoint:** `/arch-api/architectures/{arch_id}/versions/latest`
- **Method:** `GET`
- **Success Response:** Returns the architecture version object with the highest version number.

## Interaction Example (using Python with `requests`)

```python
import requests
import json

GATEWAY_URL = "http://localhost"

try:
    # --- 1. Create an Architecture Family ---
    arch_family_payload = {
        "project_id": 1, # Assume project 1 exists
        "name": "Payment Gateway Architecture"
    }
    create_family_resp = requests.post(f"{GATEWAY_URL}/arch-api/architectures/", json=arch_family_payload)
    create_family_resp.raise_for_status()
    arch_family_data = create_family_resp.json()
    arch_id = arch_family_data['id']
    print(f"Architecture Family created with ID: {arch_id}")

    # --- 2. Create a New Version ---
    version_payload = {
        "model_data": {
            "description": "Initial design using Stripe.",
            "components": ["API Endpoint", "Stripe SDK", "Webhook Handler"]
        }
    }
    create_version_url = f"{GATEWAY_URL}/arch-api/architectures/{arch_id}/versions/"
    create_version_resp = requests.post(create_version_url, json=version_payload)
    create_version_resp.raise_for_status()
    version_data = create_version_resp.json()
    print("New version created:", json.dumps(version_data, indent=2))

    # --- 3. Retrieve the Latest Version ---
    get_latest_url = f"{GATEWAY_URL}/arch-api/architectures/{arch_id}/versions/latest"
    get_latest_resp = requests.get(get_latest_url)
    get_latest_resp.raise_for_status()
    latest_version_data = get_latest_resp.json()
    print("Retrieved latest version:", json.dumps(latest_version_data, indent=2))

except requests.exceptions.RequestException as e:
    print(f"An API error occurred: {e}")

```
