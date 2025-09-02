from sqlalchemy.orm import Session
from . import models, schemas

def create_artifact_mapping(db: Session, mapping: schemas.ArtifactMappingCreate):
    """
    Saves a new artifact mapping to the database.
    """
    db_mapping = models.ArtifactMapping(
        internal_id=mapping.internal_id,
        external_id=mapping.external_id,
        external_parent_id=mapping.external_parent_id,
        source_service=mapping.source_service,
        external_tool=mapping.external_tool
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

def get_mapping_by_internal_id(db: Session, internal_id: str, external_tool: str):
    """
    Retrieves a mapping from the database using the internal artifact ID.
    """
    return db.query(models.ArtifactMapping).filter(
        models.ArtifactMapping.internal_id == internal_id,
        models.ArtifactMapping.external_tool == external_tool
    ).first()

def get_mapping_by_external_id(db: Session, external_id: str, external_tool: str):
    """
    Retrieves a mapping from the database using the external artifact ID.
    """
    return db.query(models.ArtifactMapping).filter(
        models.ArtifactMapping.external_id == external_id,
        models.ArtifactMapping.external_tool == external_tool
    ).first()

def get_all_mappings(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves all artifact mappings from the database.
    """
    return db.query(models.ArtifactMapping).offset(skip).limit(limit).all()
