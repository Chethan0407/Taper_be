from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime
from app.api import deps
from app.schemas.checklist_template import (
    ChecklistTemplateCreate, ChecklistTemplateOut, ChecklistItemCreate, ChecklistItemOut,
    ActiveChecklistCreate, ActiveChecklistOut, ActiveChecklistItemCreate, ActiveChecklistItemOut, ActiveChecklistItemUpdate
)
from app.db.models import ChecklistTemplate, ChecklistItem, ActiveChecklist, ActiveChecklistItem
from app.core.logging import get_logger, log_audit_event
from app.utils.security import get_current_user
from app.schemas.user import UserOut
import app.db.models as models

router = APIRouter()

logger = get_logger(__name__)

# --- Checklist Templates ---
@router.post("/templates", response_model=ChecklistTemplateOut)
def create_checklist_template(
    template: ChecklistTemplateCreate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Create a new checklist template."""
    db_template = ChecklistTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    # Audit logging
    log_audit_event(
        logger=logger,
        event_type="checklist_template_created",
        user_id=current_user.id,
        resource_type="checklist_template",
        resource_id=db_template.id,
        action="create",
        details={"name": template.name, "created_by": template.created_by}
    )
    
    return db_template

@router.get("/templates", response_model=List[ChecklistTemplateOut])
def get_checklist_templates(
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get all checklist templates."""
    templates = db.query(ChecklistTemplate).all()
    return templates

# --- Checklist Items ---
@router.post("/templates/{template_id}/items", response_model=ChecklistItemOut)
def add_item_to_template(
    template_id: int,
    item: ChecklistItemCreate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Add an item to a checklist template."""
    # Check if template exists
    template = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db_item = ChecklistItem(**item.dict(), template_id=template_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Audit logging
    log_audit_event(
        logger=logger,
        event_type="checklist_item_created",
        user_id=current_user.id,
        resource_type="checklist_item",
        resource_id=db_item.id,
        action="create",
        details={"template_id": template_id, "title": item.title, "order": item.order}
    )
    
    return db_item

@router.get("/templates/{template_id}/items", response_model=List[ChecklistItemOut])
def get_template_items(
    template_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get all items for a checklist template."""
    items = db.query(ChecklistItem).filter(ChecklistItem.template_id == template_id).all()
    return items

# --- Active Checklists ---
@router.post("/active", response_model=ActiveChecklistOut)
def create_active_checklist(
    checklist: ActiveChecklistCreate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Create an active checklist from a template."""
    # Check if template exists
    template = db.query(ChecklistTemplate).filter(ChecklistTemplate.id == checklist.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create active checklist
    db_checklist = ActiveChecklist(**checklist.dict())
    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)
    
    # Create active items from template items
    template_items = db.query(ChecklistItem).filter(ChecklistItem.template_id == checklist.template_id).all()
    for template_item in template_items:
        active_item = ActiveChecklistItem(
            checklist_id=db_checklist.id,
            template_item_id=template_item.id,
            status="pending"
        )
        db.add(active_item)
    
    db.commit()
    
    # Audit logging
    log_audit_event(
        logger=logger,
        event_type="active_checklist_created",
        user_id=current_user.id,
        resource_type="active_checklist",
        resource_id=db_checklist.id,
        action="create",
        details={"template_id": checklist.template_id, "linked_spec_id": checklist.linked_spec_id}
    )
    
    return db_checklist

@router.get("/active", response_model=List[ActiveChecklistOut])
def get_active_checklists(
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get all active checklists."""
    checklists = db.query(ActiveChecklist).all()
    return checklists

@router.get("/active/{checklist_id}/items", response_model=List[ActiveChecklistItemOut])
def get_active_checklist_items(
    checklist_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get all items for an active checklist."""
    items = db.query(ActiveChecklistItem).filter(ActiveChecklistItem.checklist_id == checklist_id).all()
    return items

@router.patch("/active/{checklist_id}/items/{item_id}", response_model=ActiveChecklistItemOut)
def update_checklist_item(
    checklist_id: int,
    item_id: int,
    item_update: ActiveChecklistItemUpdate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Update a checklist item (status, comment, assignment). Only assigned users or admins can update."""
    db_item = db.query(ActiveChecklistItem).filter(
        ActiveChecklistItem.id == item_id,
        ActiveChecklistItem.checklist_id == checklist_id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    # Authorization check: only assigned user or admin can update
    if (db_item.assigned_to_user_id and 
        db_item.assigned_to_user_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=403, 
            detail="Only assigned users or admins can update this checklist item"
        )
    
    # Update fields
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    
    # Audit logging
    log_audit_event(
        logger=logger,
        event_type="checklist_item_updated",
        user_id=current_user.id,
        resource_type="active_checklist_item",
        resource_id=db_item.id,
        action="update",
        details=update_data
    )
    
    return db_item

# --- Evidence Upload ---
@router.post("/active/{checklist_id}/items/{item_id}/evidence", response_model=ActiveChecklistItemOut)
async def upload_evidence(
    checklist_id: int,
    item_id: int,
    file: UploadFile = File(...),
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Upload evidence file for a checklist item with atomic file save and DB update. Only assigned users or admins can upload."""
    try:
        # Validate file type and size
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.doc', '.docx'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (max 10MB)
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Get the checklist item
        checklist_item = db.query(ActiveChecklistItem).filter(
            ActiveChecklistItem.id == item_id,
            ActiveChecklistItem.checklist_id == checklist_id
        ).first()
        
        if not checklist_item:
            raise HTTPException(status_code=404, detail="Checklist item not found")
        
        # Authorization check: only assigned user or admin can upload evidence
        if (checklist_item.assigned_to_user_id and 
            checklist_item.assigned_to_user_id != current_user.id and 
            current_user.role != "admin"):
            raise HTTPException(
                status_code=403, 
                detail="Only assigned users or admins can upload evidence for this checklist item"
            )
        
        # Create upload directory if it doesn't exist
        upload_dir = "uploads/checklist_evidence"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Atomic operation: save file first, then update DB
        try:
            # Save file to disk
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Update database
            checklist_item.evidence_file_path = file_path
            checklist_item.updated_at = datetime.utcnow()
            db.commit()
            
            # Audit logging for successful upload
            log_audit_event(
                logger=logger,
                event_type="evidence_file_uploaded",
                user_id=current_user.id,
                resource_type="active_checklist_item",
                resource_id=item_id,
                action="upload_evidence",
                details={"filename": file.filename, "file_size": file_size, "file_path": file_path}
            )
            
            return checklist_item
            
        except Exception as e:
            # Rollback: delete file if it was created
            if os.path.exists(file_path):
                os.remove(file_path)
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save evidence: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        # Audit logging for failed upload
        log_audit_event(
            logger=logger,
            event_type="evidence_file_upload_failed",
            user_id=current_user.id,
            resource_type="active_checklist_item",
            resource_id=item_id,
            action="upload_evidence_failed",
            details={"filename": file.filename, "error": str(e)}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

# --- Completion Percentage ---
@router.get("/active/{checklist_id}/completion")
def get_completion_percent(checklist_id: int, db: Session = Depends(deps.get_db)):
    total = db.query(ActiveChecklistItem).filter(ActiveChecklistItem.checklist_id == checklist_id).count()
    done = db.query(ActiveChecklistItem).filter(ActiveChecklistItem.checklist_id == checklist_id, ActiveChecklistItem.status == "done").count()
    percent = (done / total * 100) if total else 0
    return {"completion_percent": percent} 

# --- Assignment Endpoints ---
@router.post("/active/{checklist_id}/items/{item_id}/assign")
def assign_user_to_item(
    checklist_id: int,
    item_id: int,
    user_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Assign a user to a checklist item. Only admins or checklist creators can assign users."""
    db_item = db.query(ActiveChecklistItem).filter(
        ActiveChecklistItem.id == item_id,
        ActiveChecklistItem.checklist_id == checklist_id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Authorization: only admins or checklist creators can assign
    checklist = db.query(ActiveChecklist).filter(ActiveChecklist.id == checklist_id).first()
    if (current_user.role != "admin" and 
        checklist.created_by != current_user.email):
        raise HTTPException(
            status_code=403, 
            detail="Only admins or checklist creators can assign users"
        )
    
    # Update assignment
    db_item.assigned_to_user_id = user_id
    db_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    
    # Audit logging
    log_audit_event(
        logger=logger,
        event_type="checklist_item_assigned",
        user_id=current_user.id,
        resource_type="active_checklist_item",
        resource_id=db_item.id,
        action="assign_user",
        details={"assigned_user_id": user_id, "assigned_user_email": user.email}
    )
    
    return {"msg": f"User {user.email} assigned to checklist item", "item": db_item}

@router.get("/active/assigned-to/{user_id}")
def get_items_assigned_to_user(
    user_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get all checklist items assigned to a specific user."""
    # Authorization: users can only see their own assignments, admins can see all
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="You can only view your own assignments"
        )
    
    items = db.query(ActiveChecklistItem).filter(
        ActiveChecklistItem.assigned_to_user_id == user_id
    ).all()
    
    return items

@router.get("/active/{checklist_id}/assignments")
def get_checklist_assignments(
    checklist_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get all users assigned to items in a specific checklist."""
    # Check if checklist exists
    checklist = db.query(ActiveChecklist).filter(ActiveChecklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    # Get all items with assignments for this checklist
    items_with_assignments = db.query(ActiveChecklistItem).filter(
        ActiveChecklistItem.checklist_id == checklist_id,
        ActiveChecklistItem.assigned_to_user_id.isnot(None)
    ).all()
    
    # Get unique assigned users
    assigned_user_ids = list(set([item.assigned_to_user_id for item in items_with_assignments]))
    assigned_users = db.query(models.User).filter(models.User.id.in_(assigned_user_ids)).all()
    
    return {
        "checklist_id": checklist_id,
        "assigned_users": assigned_users,
        "items_with_assignments": items_with_assignments
    } 