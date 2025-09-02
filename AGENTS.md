# Top-Level Agent Instructions

## High-Level Goal

Welcome, agent. Your primary goal when interacting with this repository is to manage the software development lifecycle (SDLC) for a software project. This involves creating project artifacts, running AI-powered analyses, and integrating with external tools.

This platform is a **microservices ecosystem**. You do not interact with the code of individual services directly. Instead, you must interact with their APIs through the central **API Gateway**.

## Core Principles for Agents

1.  **API-First Interaction:** All operations must be performed by making HTTP requests to the appropriate service API via the gateway. Do not attempt to modify the database or file storage directly.
2.  **Sequential Workflow:** The platform is designed to be used in a specific sequence. For example, you must create a project before you can upload a document to it.
3.  **Consult Service-Specific Documentation:** This file provides the high-level overview. For detailed instructions on how to interact with a specific service, you **must** read the `AGENTS.md` file located in that service's subdirectory.

## Getting Started: A Typical Workflow

Here is the standard operational flow for an agent to generate requirements for a new project:

1.  **Create a Project:**
    - **Goal:** Establish a new project container for all subsequent artifacts.
    - **Service:** `project-input-service`
    - **Action:** Read `project-input-service/AGENTS.md` and make a `POST` request to its `/projects/` endpoint.
    - **Output:** A project object containing a unique `project_id`. **You must store this ID.**

2.  **Upload a Document:**
    - **Goal:** Provide a source document (e.g., requirements in a PDF or DOCX file) for analysis.
    - **Service:** `project-input-service`
    - **Action:** Read `project-input-service/AGENTS.md` and make a `POST` request to its `/projects/{project_id}/documents/` endpoint, using the ID from the previous step.
    - **Output:** Confirmation of the file upload.

3.  **Trigger AI Analysis (Requirements Generation):**
    - **Goal:** Instruct an AI agent service to process the uploaded document.
    - **Service:** `requirements-agent-service`
    - **Action:** This is a two-step process. Read `requirements-agent-service/AGENTS.md` carefully.
        1.  First, call the `/ingest-document` endpoint to load the document into the vector store.
        2.  Second, call the `/generate-requirements` endpoint to start the analysis and push the results to Jira.
    - **Output:** A JSON object containing the results of the Jira push operations.

## Directory of Agent Instructions

- **[Project & Document Management](./project-input-service/AGENTS.md)**
- **[Architecture & ADR Management](./architecture-adr-service/AGENTS.md)**
- **[Jira Integration](./integration-and-sync-service/AGENTS.md)**
- **[Requirements Generation AI](./requirements-agent-service/AGENTS.md)**

Consult these files for specific API endpoint details, request bodies, and example interactions.
