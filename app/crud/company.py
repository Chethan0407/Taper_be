from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import or_

from app.db.models import Company, Project
from app.schemas.company import CompanyCreate, CompanyUpdate

def get_company(db: Session, company_id: int) -> Optional[Company]:
    return db.query(Company).filter(Company.id == company_id).first()

def get_companies(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    owner_id: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[str] = None
) -> List[Company]:
    query = db.query(Company)
    if owner_id:
        query = query.filter(Company.owner_id == owner_id)
    if search:
        from app.db.models import User
        query = query.join(User, Company.owner_id == User.id, isouter=True)
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Company.name.ilike(search_pattern),
                Company.description.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )
    if status:
        query = query.filter(Company.status == status)
    return query.offset(skip).limit(limit).all()

def create_company(db: Session, company: CompanyCreate, owner_id: int) -> Company:
    db_company = Company(
        **company.dict(),
        owner_id=owner_id
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def update_company(
    db: Session,
    company_id: int,
    company: CompanyUpdate,
    owner_id: int
) -> Optional[Company]:
    db_company = get_company(db, company_id)
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    if db_company.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    for field, value in company.dict(exclude_unset=True).items():
        setattr(db_company, field, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company

def delete_company(db: Session, company_id: int, owner_id: int) -> bool:
    db_company = get_company(db, company_id)
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    if db_company.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    # Prevent deletion if projects exist
    projects = db.query(Project).filter(Project.company_id == company_id).all()
    if projects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete company with existing projects. Please delete all projects first."
        )
    db.delete(db_company)
    db.commit()
    return True 