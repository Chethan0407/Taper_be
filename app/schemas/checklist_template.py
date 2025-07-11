from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChecklistItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int

class ChecklistItemCreate(ChecklistItemBase):
    pass

class ChecklistItemOut(ChecklistItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ChecklistTemplateBase(BaseModel):
    name: str
    created_by: Optional[str] = None

class ChecklistTemplateCreate(ChecklistTemplateBase):
    pass

class ChecklistTemplateOut(ChecklistTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ChecklistItemOut] = []
    class Config:
        from_attributes = True

class ActiveChecklistBase(BaseModel):
    template_id: int
    linked_spec_id: Optional[str] = None
    created_by: Optional[str] = None
    status: Optional[str] = "active"

class ActiveChecklistCreate(ActiveChecklistBase):
    pass

class ActiveChecklistOut(ActiveChecklistBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ActiveChecklistItemBase(BaseModel):
    status: str = "pending"
    comment: Optional[str] = None
    evidence_file_path: Optional[str] = None
    assigned_to_user_id: Optional[int] = None

class ActiveChecklistItemCreate(ActiveChecklistItemBase):
    pass

class ActiveChecklistItemUpdate(BaseModel):
    status: Optional[str] = None
    comment: Optional[str] = None
    evidence_file_path: Optional[str] = None
    assigned_to_user_id: Optional[int] = None

class ActiveChecklistItemOut(ActiveChecklistItemBase):
    id: int
    checklist_id: int
    template_item_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True 