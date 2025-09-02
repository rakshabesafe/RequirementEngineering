from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from . import models, schemas

#--------------------------------------------------------------------------
# CRUD for Architecture (the parent object)
#--------------------------------------------------------------------------

def create_architecture(db: Session, architecture: schemas.ArchitectureCreate):
    db_architecture = models.Architecture(
        project_id=architecture.project_id,
        name=architecture.name
    )
    db.add(db_architecture)
    db.commit()
    db.refresh(db_architecture)
    return db_architecture

def get_architecture(db: Session, architecture_id: int):
    return db.query(models.Architecture).filter(models.Architecture.id == architecture_id).first()

def get_architecture_by_name(db: Session, project_id: int, name: str):
    return db.query(models.Architecture).filter(
        models.Architecture.project_id == project_id,
        models.Architecture.name == name
    ).first()

def get_architectures(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Architecture).offset(skip).limit(limit).all()


#--------------------------------------------------------------------------
# CRUD for ArchitectureVersion
#--------------------------------------------------------------------------

def create_architecture_version(db: Session, architecture_id: int, version_data: schemas.ArchitectureVersionCreate):
    # Find the latest version number for this architecture_id
    latest_version = db.query(func.max(models.ArchitectureVersion.version)).filter(
        models.ArchitectureVersion.architecture_id == architecture_id
    ).scalar()

    new_version_number = 1 if latest_version is None else latest_version + 1

    db_version = models.ArchitectureVersion(
        architecture_id=architecture_id,
        version=new_version_number,
        model_data=version_data.model_data
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

def get_architecture_versions(db: Session, architecture_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ArchitectureVersion).filter(
        models.ArchitectureVersion.architecture_id == architecture_id
    ).order_by(desc(models.ArchitectureVersion.version)).offset(skip).limit(limit).all()

def get_architecture_version(db: Session, architecture_id: int, version: int):
    return db.query(models.ArchitectureVersion).filter(
        models.ArchitectureVersion.architecture_id == architecture_id,
        models.ArchitectureVersion.version == version
    ).first()

def get_latest_architecture_version(db: Session, architecture_id: int):
    return db.query(models.ArchitectureVersion).filter(
        models.ArchitectureVersion.architecture_id == architecture_id
    ).order_by(desc(models.ArchitectureVersion.version)).first()
