from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.db.models import Company, Project, Spec
from app.schemas.user import UserOut
from app.schemas.company import Company as CompanySchema
from app.schemas.project import Project as ProjectSchema
from app.schemas.spec import Spec as SpecSchema

router = APIRouter()

@router.get("/", response_model=dict)
def global_search(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    companies = db.query(Company).filter(Company.name.ilike(f"%{q}%")).all()
    projects = db.query(Project).filter(Project.name.ilike(f"%{q}%")).all()
    specs = db.query(Spec).filter(Spec.name.ilike(f"%{q}%")).all()
    return {
        "companies": [CompanySchema.model_validate(c).model_dump() for c in companies],
        "projects": [ProjectSchema.model_validate(p).model_dump() for p in projects],
        "specs": [SpecSchema.model_validate(s).model_dump() for s in specs],
    } 