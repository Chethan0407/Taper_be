from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[dict])
def list_notifications(db: Session = Depends(deps.get_db)):
    """
    List all notifications (placeholder implementation).
    """
    # Placeholder: Replace with actual DB query
    return [] 