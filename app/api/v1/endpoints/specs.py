from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import spec as crud_spec
from app.crud import lint_result as crud_lint
from app.schemas.spec import Spec, SpecCreate, SpecUpdate, SpecWithLintResults
from app.schemas.lint_result import LintResult, LintResultCreate
from app.schemas.user import UserOut
from app.services.lint import lint_spec

router = APIRouter()

@router.get("/projects/{project_id}/specs", response_model=List[Spec])
def read_specs(
    project_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Retrieve specs for a project.
    """
    specs = crud_spec.get_specs(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit
    )
    return specs

@router.post("/projects/{project_id}/specs", response_model=Spec)
async def create_spec(
    project_id: int,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(None),
    version: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Create new spec for a project.
    """
    spec_in = SpecCreate(
        project_id=project_id,
        name=name,
        description=description,
        version=version
    )
    spec = await crud_spec.create_spec(
        db=db,
        spec_in=spec_in,
        file=file,
        author_id=current_user.id
    )
    return spec

@router.get("/specs/{spec_id}", response_model=SpecWithLintResults)
def read_spec(
    spec_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get spec by ID.
    """
    spec = crud_spec.get_spec(db=db, spec_id=spec_id)
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found"
        )
    return spec

@router.put("/specs/{spec_id}", response_model=Spec)
def update_spec(
    spec_id: int,
    spec_in: SpecUpdate,
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Update a spec.
    """
    spec = crud_spec.update_spec(
        db=db,
        spec_id=spec_id,
        spec_in=spec_in,
        company_owner_id=current_user.id
    )
    return spec

@router.delete("/specs/{spec_id}", response_model=bool)
def delete_spec(
    spec_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Delete a spec.
    """
    return crud_spec.delete_spec(
        db=db,
        spec_id=spec_id,
        company_owner_id=current_user.id
    )

@router.post("/specs/{spec_id}/lint", response_model=LintResult)
async def trigger_lint(
    spec_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Trigger linting on a spec.
    """
    spec = crud_spec.get_spec(db=db, spec_id=spec_id)
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found"
        )
    
    # Run linting
    lint_result = await lint_spec(spec)
    
    # Save result
    db_lint_result = crud_lint.create_lint_result(
        db=db,
        lint_result_in=LintResultCreate(
            spec_id=spec_id,
            issues=lint_result.issues,
            summary=lint_result.summary
        ),
        company_owner_id=current_user.id
    )
    return db_lint_result

@router.get("/specs/{spec_id}/lint-results", response_model=List[LintResult])
def read_lint_results(
    spec_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get lint results for a spec.
    """
    results = crud_lint.get_lint_results(
        db=db,
        spec_id=spec_id,
        skip=skip,
        limit=limit
    )
    return results

@router.post("/specs", response_model=dict)
def upload_spec(db: Session = Depends(deps.get_db)):
    """Upload new spec (placeholder)."""
    return {"msg": "Spec uploaded"}

@router.get("/specs/{spec_id}/versions", response_model=dict)
def get_spec_versions(spec_id: int, db: Session = Depends(deps.get_db)):
    """Get spec version history (placeholder)."""
    return {"msg": "Version history"}

@router.get("/specs/{spec_id}/compare", response_model=dict)
def compare_spec_versions(spec_id: int, to: str, db: Session = Depends(deps.get_db)):
    """Compare spec versions (placeholder)."""
    return {"msg": "Comparison result"}

@router.post("/specs/{spec_id}/reviewers", response_model=dict)
def assign_reviewers(spec_id: int, db: Session = Depends(deps.get_db)):
    """Assign reviewers (placeholder)."""
    return {"msg": "Reviewers assigned"}

@router.delete("/specs/{spec_id}/reviewers/{reviewer_id}", response_model=dict)
def remove_reviewer(spec_id: int, reviewer_id: int, db: Session = Depends(deps.get_db)):
    """Remove reviewer (placeholder)."""
    return {"msg": "Reviewer removed"}

@router.post("/specs/{spec_id}/approve", response_model=dict)
def approve_spec(spec_id: int, db: Session = Depends(deps.get_db)):
    """Approve spec (placeholder)."""
    return {"msg": "Spec approved"}

@router.get("/specs/{spec_id}/download", response_model=dict)
def download_spec(spec_id: int, db: Session = Depends(deps.get_db)):
    """Download/export spec (placeholder)."""
    return {"msg": "Spec downloaded"}

@router.post("/specs/{spec_id}/duplicate", response_model=dict)
def duplicate_spec(spec_id: int, db: Session = Depends(deps.get_db)):
    """Duplicate/copy spec (placeholder)."""
    return {"msg": "Spec duplicated"} 