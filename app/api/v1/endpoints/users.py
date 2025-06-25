from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(deps.get_db)):
    """
    List all users (placeholder implementation).
    """
    # Placeholder: Replace with actual DB query
    return [] 