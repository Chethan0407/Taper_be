from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import company as crud
from app.schemas.company import Company, CompanyCreate, CompanyUpdate
from app.schemas.user import UserOut
from app.db.models import User

router = APIRouter()

def get_user_email(db, user_id):
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    return user.email if user else None

@router.get("/", response_model=List[Company])
def read_companies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None, description="Search companies by name, description, or creator email"),
    status: str = Query(None, description="Filter companies by status (Active, Inactive, etc.)"),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Retrieve companies, optionally filtered by search query and status.
    """
    companies = crud.get_companies(
        db=db,
        skip=skip,
        limit=limit,
        owner_id=current_user.id,
        search=search,
        status=status
    )
    result = []
    for company in companies:
        company_data = company.__dict__.copy()
        company_data["created_by"] = get_user_email(db, company.owner_id)
        company_data["updated_by"] = get_user_email(db, company.owner_id)  # If you add updated_by_id, use that here
        result.append(company_data)
    return result

@router.post("/", response_model=Company)
def create_company(
    *,
    db: Session = Depends(deps.get_db),
    company_in: CompanyCreate,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Create new company.
    """
    company = crud.create_company(
        db=db,
        company=company_in,
        owner_id=current_user.id
    )
    company_data = company.__dict__.copy()
    company_data["created_by"] = current_user.email
    company_data["updated_by"] = current_user.email
    return company_data

@router.get("/{company_id}", response_model=Company)
def read_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get company by ID.
    """
    company = crud.get_company(db=db, company_id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    if company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    company_data = company.__dict__.copy()
    company_data["created_by"] = get_user_email(db, company.owner_id)
    company_data["updated_by"] = get_user_email(db, company.owner_id)  # If you add updated_by_id, use that here
    return company_data

@router.put("/{company_id}", response_model=Company)
def update_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    company_in: CompanyUpdate,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Update a company.
    """
    company = crud.update_company(
        db=db,
        company_id=company_id,
        company=company_in,
        owner_id=current_user.id
    )
    company_data = company.__dict__.copy()
    company_data["created_by"] = get_user_email(db, company.owner_id)
    company_data["updated_by"] = current_user.email
    return company_data

@router.delete("/{company_id}", response_model=bool)
def delete_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: int,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Delete a company.
    """
    return crud.delete_company(
        db=db,
        company_id=company_id,
        owner_id=current_user.id
    ) 