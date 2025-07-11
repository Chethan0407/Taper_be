from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class SpecificationBase(BaseModel):
    file_name: str
    mime_type: str
    uploaded_by: str
    status: Optional[str] = "Pending"
    assigned_to: Optional[str] = None
    file_path: str

class SpecificationCreate(SpecificationBase):
    pass

class SpecificationOut(SpecificationBase):
    id: UUID
    uploaded_on: datetime

    class Config:
        orm_mode = True 