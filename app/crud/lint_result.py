from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import LintResult, Spec, Project, Company
from app.schemas.lint_result import LintResultCreate

def get_lint_result(db: Session, lint_result_id: int) -> Optional[LintResult]:
    return db.query(LintResult).filter(LintResult.id == lint_result_id).first()

def get_lint_results(
    db: Session,
    spec_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[LintResult]:
    return db.query(LintResult)\
        .filter(LintResult.spec_id == spec_id)\
        .order_by(LintResult.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_lint_result(
    db: Session,
    lint_result_in: LintResultCreate,
    company_owner_id: int
) -> LintResult:
    # Verify spec exists and user has access
    spec = db.query(Spec).filter(Spec.id == lint_result_in.spec_id).first()
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found"
        )
    
    # Verify user owns the company
    project = db.query(Project).filter(Project.id == spec.project_id).first()
    company = db.query(Company).filter(Company.id == project.company_id).first()
    if company.owner_id != company_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_lint_result = LintResult(**lint_result_in.dict())
    db.add(db_lint_result)
    db.commit()
    db.refresh(db_lint_result)
    return db_lint_result

def delete_lint_result(
    db: Session,
    lint_result_id: int,
    company_owner_id: int
) -> bool:
    db_lint_result = get_lint_result(db, lint_result_id)
    if not db_lint_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lint result not found"
        )
    
    # Verify user owns the company
    spec = db.query(Spec).filter(Spec.id == db_lint_result.spec_id).first()
    project = db.query(Project).filter(Project.id == spec.project_id).first()
    company = db.query(Company).filter(Company.id == project.company_id).first()
    if company.owner_id != company_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(db_lint_result)
    db.commit()
    return True 