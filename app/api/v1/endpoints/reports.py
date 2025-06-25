from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO
import json
from datetime import datetime

from app.api import deps
from app.services import report as report_service
from app.schemas.report import (
    ReportFilters,
    ProjectSummary,
    SpecSummary,
    LintSummary,
    CommentSummary,
    SystemUsage,
    ExportFormat
)
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/reports/projects", response_model=ProjectSummary)
def get_project_report(
    db: Session = Depends(deps.get_db),
    start_date: datetime = None,
    end_date: datetime = None,
    company_id: int = None,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get project summary report.
    """
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        company_id=company_id
    )
    return report_service.get_project_summary(
        db=db,
        filters=filters,
        company_owner_id=current_user.id
    )

@router.get("/reports/specs", response_model=SpecSummary)
def get_spec_report(
    db: Session = Depends(deps.get_db),
    start_date: datetime = None,
    end_date: datetime = None,
    project_id: int = None,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get spec summary report.
    """
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        project_id=project_id
    )
    return report_service.get_spec_summary(
        db=db,
        filters=filters,
        company_owner_id=current_user.id
    )

@router.get("/reports/linting", response_model=LintSummary)
def get_lint_report(
    db: Session = Depends(deps.get_db),
    start_date: datetime = None,
    end_date: datetime = None,
    project_id: int = None,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get lint summary report.
    """
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        project_id=project_id
    )
    return report_service.get_lint_summary(
        db=db,
        filters=filters,
        company_owner_id=current_user.id
    )

@router.get("/reports/comments", response_model=CommentSummary)
def get_comment_report(
    db: Session = Depends(deps.get_db),
    start_date: datetime = None,
    end_date: datetime = None,
    project_id: int = None,
    user_id: int = None,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get comment summary report.
    """
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        user_id=user_id
    )
    return report_service.get_comment_summary(
        db=db,
        filters=filters,
        company_owner_id=current_user.id
    )

@router.get("/reports/usage", response_model=SystemUsage)
def get_usage_report(
    db: Session = Depends(deps.get_db),
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Get system usage report.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date
    )
    return report_service.get_system_usage(
        db=db,
        filters=filters,
        company_owner_id=current_user.id
    )

@router.get("/reports/export")
def export_report(
    report_type: str = Query(..., description="Type of report (projects/specs/linting/comments/usage)"),
    format: ExportFormat = Query(..., description="Export format (csv/pdf)"),
    db: Session = Depends(deps.get_db),
    start_date: datetime = None,
    end_date: datetime = None,
    project_id: int = None,
    company_id: int = None,
    user_id: int = None,
    current_user: UserOut = Depends(deps.get_current_user)
):
    """
    Export report data.
    """
    filters = ReportFilters(
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        company_id=company_id,
        user_id=user_id
    )
    
    # Get report data
    if report_type == "projects":
        data = report_service.get_project_summary(db, filters, current_user.id)
    elif report_type == "specs":
        data = report_service.get_spec_summary(db, filters, current_user.id)
    elif report_type == "linting":
        data = report_service.get_lint_summary(db, filters, current_user.id)
    elif report_type == "comments":
        data = report_service.get_comment_summary(db, filters, current_user.id)
    elif report_type == "usage":
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        data = report_service.get_system_usage(db, filters, current_user.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report type"
        )
    
    # Export data
    if format == ExportFormat.CSV:
        # Convert data to CSV
        df = pd.json_normalize(data)
        output = StringIO()
        df.to_csv(output, index=False)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={report_type}_report.csv"
            }
        )
    else:
        # Convert data to PDF (placeholder - implement PDF generation)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF export not implemented yet"
        ) 