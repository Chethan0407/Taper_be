from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import project as crud
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/", response_model=List[Project])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    company_id: int | None = None,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Retrieve projects.
    """
    projects = crud.get_projects(
        db=db,
        skip=skip,
        limit=limit,
        company_id=company_id
    )
    return projects

@router.post("/", response_model=Project)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Create new project.
    """
    project = crud.create_project(
        db=db,
        project=project_in,
        company_owner_id=current_user.id
    )
    return project

@router.get("/{project_id}", response_model=Project)
def read_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get project by ID.
    """
    project = crud.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.put("/{project_id}", response_model=Project)
def update_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    project_in: ProjectUpdate,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Update a project.
    """
    project = crud.update_project(
        db=db,
        project_id=project_id,
        project=project_in,
        company_owner_id=current_user.id
    )
    return project

@router.delete("/{project_id}", response_model=bool)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Delete a project.
    """
    return crud.delete_project(
        db=db,
        project_id=project_id,
        company_owner_id=current_user.id
    ) 