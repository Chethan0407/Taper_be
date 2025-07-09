from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from enum import Enum
import shutil
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploaded_specs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SpecStatus(str, Enum):
    APPROVED = "Approved"
    PENDING = "Pending"
    REJECTED = "Rejected"

class SpecFile:
    def __init__(self, id, name, file_type, status, uploaded_by, created_at, path):
        self.id = id
        self.name = name
        self.file_type = file_type
        self.status = status
        self.uploaded_by = uploaded_by
        self.created_at = created_at
        self.path = path

spec_files: List[SpecFile] = []

@router.post("/upload", status_code=201)
async def upload_specification(
    file: UploadFile = File(...),
    name: str = Form(...),
    status: SpecStatus = Form(SpecStatus.PENDING),
    uploaded_by: str = Form(...)
):
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.openxmlformats-officedocument.presentationml.presentation"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    # Check file size (max 50MB)
    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large.")
    # Reset file pointer for further use
    file.file.seek(0)
    file_id = len(spec_files) + 1
    ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(UPLOAD_DIR, f"spec_{file_id}{ext}")
    with open(save_path, "wb") as buffer:
        buffer.write(contents)
    spec = SpecFile(
        id=file_id,
        name=name,
        file_type=file.content_type,
        status=status.value,
        uploaded_by=uploaded_by,
        created_at=datetime.utcnow(),
        path=save_path
    )
    spec_files.append(spec)
    return {"id": spec.id, "name": spec.name, "file_type": spec.file_type, "status": spec.status, "uploaded_by": spec.uploaded_by, "created_at": spec.created_at}

@router.get("/", response_model=List[dict])
def list_specifications(status: Optional[SpecStatus] = Query(None)):
    result = [
        {"id": s.id, "name": s.name, "file_type": s.file_type, "status": s.status, "uploaded_by": s.uploaded_by, "created_at": s.created_at}
        for s in spec_files if status is None or s.status == status.value
    ]
    return result

@router.get("/{id}/download")
def download_specification(id: int):
    spec = next((s for s in spec_files if s.id == id), None)
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found.")
    return FileResponse(spec.path, filename=spec.name)

@router.delete("/{id}", status_code=204)
def delete_specification(id: int):
    global spec_files
    spec = next((s for s in spec_files if s.id == id), None)
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found.")
    try:
        os.remove(spec.path)
    except Exception:
        pass
    spec_files = [s for s in spec_files if s.id != id]
    return

@router.get("/statuses", response_model=List[str])
def get_statuses():
    return [e.value for e in SpecStatus] 