from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

class Architecture(Base):
    """
    Represents a family of architectural designs for a specific component
    or system within a project.
    """
    __tablename__ = "architectures"

    id = Column(Integer, primary_key=True, index=True)
    # In a real system, this would be a foreign key to the projects table
    # in the project-input-service. For this implementation, we'll store it as an integer.
    project_id = Column(Integer, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint('project_id', 'name', name='_project_architecture_name_uc'),)


class ArchitectureVersion(Base):
    """
    Represents a specific, immutable version of an architectural design.
    A change to an architecture results in a new version, not an update.
    """
    __tablename__ = "architecture_versions"

    id = Column(Integer, primary_key=True, index=True)
    architecture_id = Column(Integer, ForeignKey("architectures.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)

    # The actual architectural model, stored as JSON.
    # Using JSONB for performance and indexing capabilities in PostgreSQL.
    model_data = Column(JSONB, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint('architecture_id', 'version', name='_architecture_version_uc'),)
