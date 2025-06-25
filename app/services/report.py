from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.db.models import Project, Spec, LintResult, Comment, User, Company
from app.schemas.report import ReportFilters, TimeRange

def get_project_summary(
    db: Session,
    filters: ReportFilters,
    company_owner_id: Optional[int] = None
) -> Dict[str, Any]:
    """Generate project summary report."""
    query = db.query(Project)
    
    # Apply filters
    if filters.company_id:
        query = query.filter(Project.company_id == filters.company_id)
    if filters.start_date:
        query = query.filter(Project.created_at >= filters.start_date)
    if filters.end_date:
        query = query.filter(Project.created_at <= filters.end_date)
    
    # Get total and active projects
    total_projects = query.count()
    active_projects = query.filter(Project.specs.any()).count()
    
    # Get projects by company
    projects_by_company = {}
    company_query = db.query(
        Company.name,
        func.count(Project.id)
    ).join(Project).group_by(Company.name)
    if filters.company_id:
        company_query = company_query.filter(Company.id == filters.company_id)
    for company_name, count in company_query.all():
        projects_by_company[company_name] = count
    
    # Get recent projects
    recent_projects = []
    for project in query.order_by(Project.created_at.desc()).limit(5).all():
        recent_projects.append({
            "id": project.id,
            "name": project.name,
            "company": project.company.name,
            "created_at": project.created_at,
            "spec_count": len(project.specs)
        })
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "projects_by_company": projects_by_company,
        "recent_projects": recent_projects
    }

def get_spec_summary(
    db: Session,
    filters: ReportFilters,
    company_owner_id: Optional[int] = None
) -> Dict[str, Any]:
    """Generate spec summary report."""
    query = db.query(Spec)
    
    # Apply filters
    if filters.project_id:
        query = query.filter(Spec.project_id == filters.project_id)
    if filters.start_date:
        query = query.filter(Spec.created_at >= filters.start_date)
    if filters.end_date:
        query = query.filter(Spec.created_at <= filters.end_date)
    
    # Get total specs
    total_specs = query.count()
    
    # Get specs by status
    specs_by_status = {}
    status_query = db.query(
        Spec.status,
        func.count(Spec.id)
    ).group_by(Spec.status)
    if filters.project_id:
        status_query = status_query.filter(Spec.project_id == filters.project_id)
    for status, count in status_query.all():
        specs_by_status[status] = count
    
    # Get specs by project
    specs_by_project = {}
    project_query = db.query(
        Project.name,
        func.count(Spec.id)
    ).join(Spec).group_by(Project.name)
    if filters.project_id:
        project_query = project_query.filter(Project.id == filters.project_id)
    for project_name, count in project_query.all():
        specs_by_project[project_name] = count
    
    # Get recent updates
    recent_updates = []
    for spec in query.order_by(Spec.updated_at.desc()).limit(5).all():
        recent_updates.append({
            "id": spec.id,
            "name": spec.name,
            "project": spec.project.name,
            "status": spec.status,
            "updated_at": spec.updated_at
        })
    
    return {
        "total_specs": total_specs,
        "specs_by_status": specs_by_status,
        "specs_by_project": specs_by_project,
        "recent_updates": recent_updates
    }

def get_lint_summary(
    db: Session,
    filters: ReportFilters,
    company_owner_id: Optional[int] = None
) -> Dict[str, Any]:
    """Generate lint summary report."""
    query = db.query(LintResult)
    
    # Apply filters
    if filters.project_id:
        query = query.join(Spec).filter(Spec.project_id == filters.project_id)
    if filters.start_date:
        query = query.filter(LintResult.created_at >= filters.start_date)
    if filters.end_date:
        query = query.filter(LintResult.created_at <= filters.end_date)
    
    # Get total issues
    total_issues = 0
    issues_by_severity = {}
    issues_by_type = {}
    
    for result in query.all():
        for issue in result.issues:
            total_issues += 1
            severity = issue.get("severity", "unknown")
            issue_type = issue.get("type", "unknown")
            
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
    
    # Get issues over time
    issues_over_time = []
    time_query = db.query(
        func.date_trunc('day', LintResult.created_at).label('date'),
        func.count(LintResult.id)
    ).group_by('date').order_by('date')
    if filters.start_date:
        time_query = time_query.filter(LintResult.created_at >= filters.start_date)
    if filters.end_date:
        time_query = time_query.filter(LintResult.created_at <= filters.end_date)
    for date, count in time_query.all():
        issues_over_time.append({
            "date": date,
            "count": count
        })
    
    # Get top projects with issues
    top_projects = []
    project_query = db.query(
        Project.name,
        func.count(LintResult.id)
    ).join(Spec).join(LintResult).group_by(Project.name).order_by(func.count(LintResult.id).desc()).limit(5)
    if filters.project_id:
        project_query = project_query.filter(Project.id == filters.project_id)
    for project_name, count in project_query.all():
        top_projects.append({
            "project": project_name,
            "issue_count": count
        })
    
    return {
        "total_issues": total_issues,
        "issues_by_severity": issues_by_severity,
        "issues_by_type": issues_by_type,
        "issues_over_time": issues_over_time,
        "top_projects_with_issues": top_projects
    }

def get_comment_summary(
    db: Session,
    filters: ReportFilters,
    company_owner_id: Optional[int] = None
) -> Dict[str, Any]:
    """Generate comment summary report."""
    query = db.query(Comment)
    
    # Apply filters
    if filters.project_id:
        query = query.filter(
            or_(
                and_(Comment.entity_type == "project", Comment.entity_id == filters.project_id),
                and_(Comment.entity_type == "spec", Comment.entity_id.in_(
                    db.query(Spec.id).filter(Spec.project_id == filters.project_id)
                ))
            )
        )
    if filters.start_date:
        query = query.filter(Comment.created_at >= filters.start_date)
    if filters.end_date:
        query = query.filter(Comment.created_at <= filters.end_date)
    
    # Get total comments
    total_comments = query.count()
    
    # Get comments by entity type
    comments_by_entity = {}
    entity_query = db.query(
        Comment.entity_type,
        func.count(Comment.id)
    ).group_by(Comment.entity_type)
    if filters.project_id:
        entity_query = entity_query.filter(
            or_(
                and_(Comment.entity_type == "project", Comment.entity_id == filters.project_id),
                and_(Comment.entity_type == "spec", Comment.entity_id.in_(
                    db.query(Spec.id).filter(Spec.project_id == filters.project_id)
                ))
            )
        )
    for entity_type, count in entity_query.all():
        comments_by_entity[entity_type] = count
    
    # Get comments over time
    comments_over_time = []
    time_query = db.query(
        func.date_trunc('day', Comment.created_at).label('date'),
        func.count(Comment.id)
    ).group_by('date').order_by('date')
    if filters.start_date:
        time_query = time_query.filter(Comment.created_at >= filters.start_date)
    if filters.end_date:
        time_query = time_query.filter(Comment.created_at <= filters.end_date)
    for date, count in time_query.all():
        comments_over_time.append({
            "date": date,
            "count": count
        })
    
    # Get most active users
    active_users = []
    user_query = db.query(
        User.full_name,
        func.count(Comment.id)
    ).join(Comment).group_by(User.full_name).order_by(func.count(Comment.id).desc()).limit(5)
    if filters.user_id:
        user_query = user_query.filter(User.id == filters.user_id)
    for user_name, count in user_query.all():
        active_users.append({
            "user": user_name,
            "comment_count": count
        })
    
    return {
        "total_comments": total_comments,
        "comments_by_entity": comments_by_entity,
        "comments_over_time": comments_over_time,
        "most_active_users": active_users
    }

def get_system_usage(
    db: Session,
    filters: ReportFilters,
    company_owner_id: Optional[int] = None
) -> Dict[str, Any]:
    """Generate system usage report."""
    # Get user stats
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Get users by role
    users_by_role = {}
    role_query = db.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role)
    for role, count in role_query.all():
        users_by_role[role] = count
    
    # Get API calls over time (placeholder - implement actual API call tracking)
    api_calls_over_time = []
    
    # Get feature usage (placeholder - implement actual feature tracking)
    feature_usage = {
        "projects_created": db.query(Project).count(),
        "specs_created": db.query(Spec).count(),
        "lint_runs": db.query(LintResult).count(),
        "comments_posted": db.query(Comment).count()
    }
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "users_by_role": users_by_role,
        "api_calls_over_time": api_calls_over_time,
        "feature_usage": feature_usage
    } 