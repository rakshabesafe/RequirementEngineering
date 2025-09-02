import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db
from .adapters.jira_adapter import JiraAdapter

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Integration and Sync Service",
    description="Manages all communication with external tools, starting with Jira.",
    version="1.0.0"
)

# In a more complex app, you'd have a factory or dependency injection system
# to select the correct adapter based on the request.
# For now, we instantiate the JiraAdapter directly.
def get_jira_adapter():
    return JiraAdapter()

@app.post("/integrations/jira/issues", response_model=schemas.JiraIssueCreateResponse, status_code=201)
def create_jira_issue_endpoint(
    issue_request: schemas.JiraIssueCreateRequest,
    db: Session = Depends(get_db),
    adapter: JiraAdapter = Depends(get_jira_adapter)
):
    """
    Creates an issue in Jira and saves a mapping to our internal database.
    """
    logger.info(f"Received request to create Jira issue for internal ID: {issue_request.internal_id}")

    # 1. Check if this artifact has already been synced
    existing_mapping = crud.get_mapping_by_internal_id(db, internal_id=issue_request.internal_id, external_tool="jira")
    if existing_mapping:
        raise HTTPException(
            status_code=409,
            detail=f"Artifact with internal ID '{issue_request.internal_id}' has already been synced to Jira issue '{existing_mapping.external_id}'."
        )

    # 2. Use the adapter to create the issue in Jira
    try:
        jira_issue = adapter.create_issue(issue_data=issue_request.dict())
    except ConnectionError as e:
        logger.error(f"Jira connection error: {e}")
        raise HTTPException(status_code=503, detail=f"Could not connect to Jira. Error: {e}")
    except Exception as e:
        logger.error(f"Failed to create Jira issue: {e}")
        # The JIRA API can return detailed error messages.
        # It's good practice to inspect `e` and provide a more specific error.
        raise HTTPException(status_code=400, detail=f"Failed to create issue in Jira. Error: {e}")

    if not jira_issue or 'key' not in jira_issue:
        raise HTTPException(status_code=500, detail="Adapter returned an invalid response from Jira.")

    # 3. Create the mapping in our database
    mapping_to_create = schemas.ArtifactMappingCreate(
        internal_id=issue_request.internal_id,
        external_id=jira_issue['key'], # e.g., "PROJ-123"
        external_parent_id=issue_request.project_key,
        source_service=issue_request.source_service,
        external_tool="jira"
    )
    saved_mapping = crud.create_artifact_mapping(db, mapping=mapping_to_create)
    logger.info(f"Successfully created mapping for Jira issue {jira_issue['key']}")

    # 4. Return a detailed response
    response = schemas.JiraIssueCreateResponse(
        jira_key=jira_issue['key'],
        jira_id=jira_issue['id'],
        jira_url=jira_issue.get('self', '').replace('rest/api/2/issue', 'browse'), # Construct a user-friendly URL
        mapping=saved_mapping
    )

    return response

@app.get("/mappings", response_model=list[schemas.ArtifactMapping])
def get_all_mappings_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves all stored artifact mappings.
    """
    return crud.get_all_mappings(db, skip=skip, limit=limit)
