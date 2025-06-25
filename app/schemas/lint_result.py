from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class LintSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class LintIssue(BaseModel):
    severity: LintSeverity
    type: str
    message: str
    location: Dict[str, Any]  # Line numbers, sections, etc.
    recommendation: Optional[str] = None

class LintResultBase(BaseModel):
    spec_id: int
    issues: List[LintIssue]
    summary: Dict[str, int]  # Count by severity
    spec_metadata: Optional[Dict[str, Any]] = None

class LintResultCreate(LintResultBase):
    pass

class LintResultInDBBase(LintResultBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LintResult(LintResultInDBBase):
    pass 