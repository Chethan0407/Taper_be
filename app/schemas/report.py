from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class TimeRange(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class ExportFormat(str, Enum):
    CSV = "csv"
    PDF = "pdf"

class ProjectSummary(BaseModel):
    total_projects: int
    active_projects: int
    projects_by_status: Dict[str, int]
    projects_by_company: Dict[str, int]
    recent_projects: List[Dict[str, Any]]

class SpecSummary(BaseModel):
    total_specs: int
    specs_by_status: Dict[str, int]
    specs_by_project: Dict[str, int]
    recent_updates: List[Dict[str, Any]]

class LintSummary(BaseModel):
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_type: Dict[str, int]
    issues_over_time: List[Dict[str, Any]]
    top_projects_with_issues: List[Dict[str, Any]]

class CommentSummary(BaseModel):
    total_comments: int
    comments_by_entity: Dict[str, int]
    comments_over_time: List[Dict[str, Any]]
    most_active_users: List[Dict[str, Any]]

class SystemUsage(BaseModel):
    total_users: int
    active_users: int
    users_by_role: Dict[str, int]
    api_calls_over_time: List[Dict[str, Any]]
    feature_usage: Dict[str, int]

class ReportFilters(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_id: Optional[int] = None
    company_id: Optional[int] = None
    user_id: Optional[int] = None
    time_range: Optional[TimeRange] = None

class ReportExport(BaseModel):
    format: ExportFormat
    filters: ReportFilters
    include_charts: bool = True 