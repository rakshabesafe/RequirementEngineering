import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Architecture ADR Service",
    description="Manages architectural models and ADRs with versioning.",
    version="1.0.0"
)

#--------------------------------------------------------------------------
# Endpoints for Architecture (the parent object)
#--------------------------------------------------------------------------

@app.post("/architectures/", response_model=schemas.Architecture, status_code=201)
def create_architecture_endpoint(architecture: schemas.ArchitectureCreate, db: Session = Depends(get_db)):
    """
    Creates a new architecture family for a given project.
    This acts as a container for its versions.
    """
    db_arch = crud.get_architecture_by_name(db, project_id=architecture.project_id, name=architecture.name)
    if db_arch:
        raise HTTPException(status_code=400, detail="Architecture with this name already exists for this project.")
    return crud.create_architecture(db=db, architecture=architecture)

@app.get("/architectures/", response_model=List[schemas.Architecture])
def read_architectures_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all architecture families.
    """
    return crud.get_architectures(db, skip=skip, limit=limit)

@app.get("/architectures/{arch_id}", response_model=schemas.ArchitectureWithLatestVersion)
def read_architecture_endpoint(arch_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific architecture family, including its latest version.
    """
    db_arch = crud.get_architecture(db, architecture_id=arch_id)
    if db_arch is None:
        raise HTTPException(status_code=404, detail="Architecture not found.")

    latest_version = crud.get_latest_architecture_version(db, architecture_id=arch_id)

    # Use the dedicated response schema
    response = schemas.ArchitectureWithLatestVersion(
        **db_arch.__dict__,
        latest_version=latest_version
    )
    return response

#--------------------------------------------------------------------------
# Endpoints for Architecture Versions
#--------------------------------------------------------------------------

@app.post("/architectures/{arch_id}/versions/", response_model=schemas.ArchitectureVersion, status_code=201)
def create_architecture_version_endpoint(arch_id: int, version_data: schemas.ArchitectureVersionCreate, db: Session = Depends(get_db)):
    """
    Creates a new, immutable version for a given architecture.
    The version number is automatically incremented.
    """
    db_arch = crud.get_architecture(db, architecture_id=arch_id)
    if db_arch is None:
        raise HTTPException(status_code=404, detail="Architecture not found. Cannot create version.")
    return crud.create_architecture_version(db=db, architecture_id=arch_id, version_data=version_data)


@app.get("/architectures/{arch_id}/versions/", response_model=List[schemas.ArchitectureVersion])
def read_architecture_versions_endpoint(arch_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieves all versions for a specific architecture, ordered from newest to oldest.
    """
    db_arch = crud.get_architecture(db, architecture_id=arch_id)
    if db_arch is None:
        raise HTTPException(status_code=404, detail="Architecture not found.")
    return crud.get_architecture_versions(db, architecture_id=arch_id, skip=skip, limit=limit)

@app.get("/architectures/{arch_id}/versions/latest", response_model=schemas.ArchitectureVersion)
def read_latest_architecture_version_endpoint(arch_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the most recent version of an architecture.
    """
    db_arch = crud.get_architecture(db, architecture_id=arch_id)
    if db_arch is None:
        raise HTTPException(status_code=404, detail="Architecture not found.")

    latest_version = crud.get_latest_architecture_version(db, architecture_id=arch_id)
    if latest_version is None:
        raise HTTPException(status_code=404, detail="No versions found for this architecture.")
    return latest_version

@app.get("/architectures/{arch_id}/versions/{version_num}", response_model=schemas.ArchitectureVersion)
def read_specific_architecture_version_endpoint(arch_id: int, version_num: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific version of an architecture by its version number.
    """
    db_version = crud.get_architecture_version(db, architecture_id=arch_id, version=version_num)
    if db_version is None:
        raise HTTPException(status_code=404, detail="Architecture version not found.")
    return db_version
