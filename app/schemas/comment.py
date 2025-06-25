from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models import EntityType

class CommentBase(BaseModel):
    content: str
    entity_type: EntityType
    entity_id: int

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: str

class CommentInDBBase(CommentBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Comment(CommentInDBBase):
    pass

class CommentWithAuthor(Comment):
    author_name: str 