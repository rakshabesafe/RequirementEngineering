from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

#--------------------------------------------------------------------------
# Schemas for Artifact Mapping
#--------------------------------------------------------------------------

class ArtifactMappingBase(BaseModel):
    internal_id: str
    external_id: str
    external_parent_id: Optional[str] = None
    source_service: str
    external_tool: str

class ArtifactMappingCreate(ArtifactMappingBase):
    pass

class ArtifactMapping(ArtifactMappingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

#--------------------------------------------------------------------------
# Schemas for Jira Integration
#--------------------------------------------------------------------------

class JiraIssueCreateRequest(BaseModel):
    """
    Defines the request body for creating a new Jira issue.
    """
    internal_id: str = Field(..., description="A unique ID for the artifact from the source service.")
    source_service: str = Field(..., description="The name of the service that originated the artifact.")
    project_key: str = Field(..., description="The project key in Jira (e.g., 'PROJ').")
    title: str = Field(..., description="The title or summary of the issue.")
    description: str = Field(..., description="The main content or description of the issue.")
    issue_type: str = Field(default="Task", description="The type of the issue in Jira (e.g., 'Task', 'Story', 'Bug').")

class JiraIssueCreateResponse(BaseModel):
    """
    Defines the response after successfully creating a Jira issue.
    """
    jira_key: str
    jira_id: str
    jira_url: str
    mapping: ArtifactMapping
