from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.specification import SpecificationOut, SpecificationCreate
from app.crud.specification import create_specification, get_specifications, get_spec_by_file_path
from app.utils.security import get_current_user
from app.schemas.user import UserOut
from typing import List, Optional
import os
import uuid
from fastapi.responses import FileResponse
from app.db.models import Specification
from datetime import datetime
from uuid import UUID

router = APIRouter()

UPLOAD_DIR = "uploaded_specs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-spec", response_model=SpecificationOut)
async def upload_spec(
    file: UploadFile = File(...),
    uploaded_by: str = Form(...),
    assigned_to: str = Form(None),
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    with open(save_path, "wb") as buffer:
        buffer.write(contents)
    spec_in = SpecificationCreate(
        file_name=file.filename,
        mime_type=file.content_type,
        uploaded_by=uploaded_by,
        assigned_to=assigned_to,
        file_path=save_path
    )
    return create_specification(db, spec_in)

@router.get("/", response_model=List[SpecificationOut])
def list_specifications(
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    file_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_specifications(
        db,
        status=status,
        assigned_to=assigned_to,
        uploaded_by=uploaded_by,
        file_type=file_type,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get("/{id}/download")
def download_specification(
    id: str,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    spec = db.query(Specification).filter(Specification.id == id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found.")
    return FileResponse(spec.file_path, filename=spec.file_name)

@router.post("/{id}/approve")
def approve_specification(
    id: str,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    spec = db.query(Specification).filter(Specification.id == id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found.")
    spec.status = "Approved"
    spec.approved_by = current_user.email
    db.commit()
    return {"msg": "Spec approved"}

@router.post("/{id}/reject")
def reject_specification(
    id: str,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    spec = db.query(Specification).filter(Specification.id == id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found.")
    spec.status = "Rejected"
    spec.rejected_by = current_user.email
    db.commit()
    return {"msg": "Spec rejected"}

@router.delete("/{id}", status_code=204)
def delete_specification(
    id: UUID,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    spec = db.query(Specification).filter(Specification.id == id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found.")
    try:
        os.remove(spec.file_path)
    except Exception:
        pass
    db.delete(spec)
    db.commit()
    return