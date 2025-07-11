from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChecklistBase(BaseModel):
    name: str
    description: Optional[str] = None

class ChecklistCreate(ChecklistBase):
    pass

class ChecklistOut(ChecklistBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 