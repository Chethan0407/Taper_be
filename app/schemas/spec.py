from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from app.schemas.lint_result import LintResult

class SpecStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ARCHIVED = "archived"

class SpecBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")  # Semantic versioning
    status: SpecStatus = SpecStatus.DRAFT
    spec_metadata: Optional[Dict[str, Any]] = None

class SpecCreate(SpecBase):
    project_id: int

class SpecUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    status: Optional[SpecStatus] = None
    spec_metadata: Optional[Dict[str, Any]] = None

class SpecInDBBase(SpecBase):
    id: int
    project_id: int
    file_path: str
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    fileUrl: Optional[str] = None

    class Config:
        from_attributes = True

class Spec(SpecInDBBase):
    pass

class SpecWithLintResults(Spec):
    lint_results: List[LintResult] = []
    fileUrl: Optional[str] = None 