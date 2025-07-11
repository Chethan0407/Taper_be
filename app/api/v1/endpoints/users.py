from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_

from app.api import deps
from app.schemas.user import UserList, UserOut
from app.db.models import User
from app.utils.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[UserList])
def list_users(
    role: Optional[str] = Query(None, description="Filter users by role (admin, engineer, pm)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    List users with optional filtering by role and active status.
    Supports pagination for frontend assignment dropdowns.
    
    - **role**: Filter by user role (admin, engineer, pm)
    - **is_active**: Filter by active status
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return (max 1000)
    """
    # Build query filters
    filters = []
    
    if role is not None:
        filters.append(User.role == role)
    
    if is_active is not None:
        filters.append(User.is_active == is_active)
    
    # Build the query
    query = db.query(User)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    return users

@router.get("/{user_id}", response_model=UserList)
def get_user(
    user_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific user by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/me/profile", response_model=UserList)
def get_my_profile(
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Get current user's full profile information.
    """
    # Get the full user object from database
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user 