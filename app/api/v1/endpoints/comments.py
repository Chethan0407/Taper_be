from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import comment as crud_comment
from app.schemas.comment import Comment, CommentCreate, CommentUpdate, CommentWithAuthor
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/comments", response_model=List[CommentWithAuthor])
def read_comments(
    entity_type: str = Query(..., description="Type of entity (spec/project/lint_result)"),
    entity_id: int = Query(..., description="ID of the entity"),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Retrieve comments for a specific entity.
    """
    comments = crud_comment.get_comments(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )
    return comments

@router.post("/comments", response_model=Comment)
def create_comment(
    comment_in: CommentCreate,
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Create new comment.
    """
    comment = crud_comment.create_comment(
        db=db,
        comment_in=comment_in,
        author_id=current_user.id
    )
    return comment

@router.put("/comments/{comment_id}", response_model=Comment)
def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Update a comment.
    """
    comment = crud_comment.update_comment(
        db=db,
        comment_id=comment_id,
        comment_in=comment_in,
        author_id=current_user.id
    )
    return comment

@router.delete("/comments/{comment_id}", response_model=bool)
def delete_comment(
    comment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Delete a comment.
    """
    return crud_comment.delete_comment(
        db=db,
        comment_id=comment_id,
        author_id=current_user.id
    ) 