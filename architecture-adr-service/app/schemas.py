from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict

#--------------------------------------------------------------------------
# Schemas for Architecture Version
#--------------------------------------------------------------------------

class ArchitectureVersionBase(BaseModel):
    model_data: Dict[str, Any] = Field(..., description="The architectural model data in JSON format.")

class ArchitectureVersionCreate(ArchitectureVersionBase):
    pass

class ArchitectureVersion(ArchitectureVersionBase):
    id: int
    architecture_id: int
    version: int
    created_at: datetime

    class Config:
        from_attributes = True

#--------------------------------------------------------------------------
# Schemas for Architecture (the parent object)
#--------------------------------------------------------------------------

class ArchitectureBase(BaseModel):
    project_id: int = Field(..., description="The ID of the project this architecture belongs to.")
    name: str = Field(..., description="A descriptive name for the architecture (e.g., 'User Service API').")

class ArchitectureCreate(ArchitectureBase):
    pass

class Architecture(ArchitectureBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ArchitectureWithLatestVersion(Architecture):
    """
    A schema that includes the parent architecture details along with its
    most recent version.
    """
    latest_version: ArchitectureVersion | None = None
