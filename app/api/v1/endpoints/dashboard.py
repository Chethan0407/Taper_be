from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.db.models import Spec
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/stats", response_model=dict)
def get_dashboard_stats(
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    active_specs = db.query(Spec).filter(Spec.status == "active").count()
    pending_reviews = db.query(Spec).filter(Spec.status == "review").count()
    vendor_partners = 0  # TODO: Replace with real count when Vendor model is implemented
    quality_score = 95  # Placeholder, can be replaced with real logic
    return {
        "active_specs": active_specs,
        "pending_reviews": pending_reviews,
        "vendor_partners": vendor_partners,
        "quality_score": quality_score
    } 