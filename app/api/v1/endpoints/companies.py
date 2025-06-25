from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import company as crud
from app.schemas.company import Company, CompanyCreate, CompanyUpdate
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/", response_model=List[Company])
def read_companies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Retrieve companies.
    """
    companies = crud.get_companies(
        db=db,
        skip=skip,
        limit=limit,
        owner_id=current_user.id
    )
    return companies

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
    return company

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
    return company

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
    return company

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