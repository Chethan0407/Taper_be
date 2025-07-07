from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.db.models import Spec, LintResult
from app.schemas.user import UserOut
import enum

class SpecStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ARCHIVED = "archived"

router = APIRouter()

@router.get("/stats", response_model=dict)
def get_dashboard_stats(
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    active_specs = db.query(Spec).filter(Spec.status == SpecStatus.APPROVED).count()
    pending_reviews = db.query(Spec).filter(Spec.status == SpecStatus.REVIEW).count()
    vendor_partners = 0  # No real Vendor model yet

    # Quality Score: % of specs with at least one LintResult and zero issues
    total_specs = db.query(Spec).count()
    if total_specs == 0:
        quality_score = 0
    else:
        passed_specs = (
            db.query(Spec)
            .join(LintResult)
            .filter(func.json_array_length(LintResult.issues) == 0)
            .distinct()
            .count()
        )
        quality_score = int((passed_specs / total_specs) * 100)

    return {
        "active_specs": active_specs,
        "pending_reviews": pending_reviews,
        "vendor_partners": vendor_partners,
        "quality_score": quality_score
    } 