import logging
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, get_db
from .minio_client import upload_file_to_minio

# It's better to use Alembic for migrations in a real app,
# but for this project, creating tables on startup is fine.
models.Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Input Service",
    description="Manages projects and ingests user documents.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    logger.info("Project Input Service is starting up.")
    # You could add checks here, e.g., to ensure DB connection is alive
    pass

@app.on_event("shutdown")
def on_shutdown():
    logger.info("Project Input Service is shutting down.")

@app.post("/projects/", response_model=schemas.Project, status_code=201)
def create_project_endpoint(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """
    Creates a new project.
    """
    db_project = crud.get_project_by_name(db, name=project.name)
    if db_project:
        raise HTTPException(status_code=400, detail=f"Project with name '{project.name}' already exists.")
    logger.info(f"Creating project: {project.name}")
    return crud.create_project(db=db, project=project)

@app.get("/projects/", response_model=list[schemas.Project])
def read_projects_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all projects.
    """
    logger.info("Fetching all projects.")
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single project by its ID.
    """
    logger.info(f"Fetching project with id: {project_id}")
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        logger.warning(f"Project with id {project_id} not found.")
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.post("/projects/{project_id}/documents/", status_code=201)
async def upload_document_endpoint(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Uploads a document to a specific project.
    The document is stored in a MinIO bucket named `project-{project_id}`.
    """
    logger.info(f"Upload request for project id: {project_id} for file: {file.filename}")
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        logger.warning(f"Upload failed: Project with id {project_id} not found.")
        raise HTTPException(status_code=404, detail="Project not found")

    # The bucket name is derived from the project ID to ensure uniqueness.
    bucket_name = f"project-{project_id}"

    try:
        contents = await file.read()
        file_size = len(contents)

        # We need to pass the file-like object, not the raw bytes.
        # So we can't use `file.file` after reading it.
        # Let's use `io.BytesIO`.
        import io
        file_stream = io.BytesIO(contents)

        storage_path = upload_file_to_minio(
            bucket_name=bucket_name,
            file_name=file.filename,
            file_data=file_stream,
            file_size=file_size
        )
        logger.info(f"File {file.filename} uploaded to {storage_path}")

        # In a real app, you would save document metadata to the DB here.
        # For now, we just return a confirmation.
        return {"filename": file.filename, "project_id": project_id, "location": storage_path}

    except ConnectionError as e:
        logger.error(f"MinIO connection error during upload for project {project_id}: {e}")
        raise HTTPException(status_code=503, detail="Could not connect to storage service.")
    except Exception as e:
        logger.error(f"An error occurred during document upload for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during file upload.")
