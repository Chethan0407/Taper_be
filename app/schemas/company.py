from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "Active"

class CompanyCreate(CompanyBase):
    status: Optional[str] = "Active"

class CompanyUpdate(CompanyBase):
    status: Optional[str] = None

class CompanyInDBBase(CompanyBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: Optional[str] = "Active"

    class Config:
        from_attributes = True

class Company(CompanyInDBBase):
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    status: Optional[str] = "Active" 