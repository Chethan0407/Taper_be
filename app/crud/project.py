from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Project, Company
from app.schemas.project import ProjectCreate, ProjectUpdate

def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None
) -> List[Project]:
    query = db.query(Project)
    if company_id:
        query = query.filter(Project.company_id == company_id)
    return query.offset(skip).limit(limit).all()

def create_project(
    db: Session,
    project: ProjectCreate,
    company_owner_id: int
) -> Project:
    # Verify company exists and user owns it
    company = db.query(Company).filter(Company.id == project.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    if company.owner_id != company_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(
    db: Session,
    project_id: int,
    project: ProjectUpdate,
    company_owner_id: int
) -> Optional[Project]:
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Verify user owns the company
    company = db.query(Company).filter(Company.id == db_project.company_id).first()
    if company.owner_id != company_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    for field, value in project.dict(exclude_unset=True).items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(
    db: Session,
    project_id: int,
    company_owner_id: int
) -> bool:
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Verify user owns the company
    company = db.query(Company).filter(Company.id == db_project.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    if company.owner_id != company_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    db.delete(db_project)
    db.commit()
    return True