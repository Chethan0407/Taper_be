from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import lint_result as crud_lint
from app.schemas.lint_result import LintResult, LintResultCreate
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/{lint_result_id}", response_model=LintResult)
def read_lint_result(
    lint_result_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get lint result by ID.
    """
    lint_result = crud_lint.get_lint_result(db=db, lint_result_id=lint_result_id)
    if not lint_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lint result not found"
        )
    return lint_result

@router.get("/spec/{spec_id}", response_model=List[LintResult])
def read_lint_results_by_spec(
    spec_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get lint results for a spec.
    """
    lint_results = crud_lint.get_lint_results(
        db=db,
        spec_id=spec_id,
        skip=skip,
        limit=limit
    )
    return lint_results 