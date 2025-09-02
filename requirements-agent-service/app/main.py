import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any

from .config import settings
from .document_processor import process_document_for_project
from .agents.requirement_generation import agent_graph, GraphState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Requirements Agent Service",
    description="Hosts AI agents for processing requirements.",
    version="1.0.0"
)

# --- API Request and Response Models ---

class DocumentIngestRequest(BaseModel):
    bucket_name: str
    object_name: str

class RequirementGenerationRequest(BaseModel):
    initial_prompt: str
    jira_project_key: str | None = None

# --- API Endpoints ---

@app.post("/projects/{project_id}/ingest-document", status_code=202)
def ingest_document_endpoint(
    project_id: int,
    request: DocumentIngestRequest,
    background_tasks: BackgroundTasks
):
    """
    Asynchronously triggers the ingestion of a document for a given project.
    The document is downloaded from MinIO, processed, and stored in the vector DB.
    """
    logger.info(f"Received request to ingest document '{request.object_name}' for project {project_id}.")

    # Run the processing in the background to avoid blocking the API response
    background_tasks.add_task(
        process_document_for_project,
        project_id,
        request.bucket_name,
        request.object_name
    )

    return {"message": "Document ingestion started in the background."}


@app.post("/projects/{project_id}/generate-requirements")
def generate_requirements_endpoint(
    project_id: int,
    request: RequirementGenerationRequest
) -> Dict[str, Any]:
    """
    Triggers the LangGraph agent to generate user stories from the
    ingested documents and push them to Jira.
    """
    logger.info(f"Received request to generate requirements for project {project_id}.")

    # Use the provided Jira project key or fall back to the default from settings
    jira_key = request.jira_project_key or settings.DEFAULT_JIRA_PROJECT_KEY
    if not jira_key:
        raise HTTPException(
            status_code=400,
            detail="Jira project key must be provided either in the request or as a default setting."
        )

    # Prepare the initial state for the graph
    initial_state: GraphState = {
        "project_id": project_id,
        "jira_project_key": jira_key,
        "initial_prompt": request.initial_prompt,
        "retrieved_docs": [],
        "generated_stories": [],
        "jira_results": [],
        "error": None,
    }

    # Invoke the agent graph. This is a synchronous call for now.
    # For long-running tasks, you would use a task queue like Celery.
    final_state = agent_graph.invoke(initial_state)

    if final_state.get("error"):
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during requirement generation: {final_state['error']}"
        )

    return {"message": "Requirement generation process completed.", "final_state": final_state}
