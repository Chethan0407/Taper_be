from sqlalchemy.orm import Session
from app.db.models import Specification
from app.schemas.specification import SpecificationCreate
from typing import List, Optional
from datetime import datetime
from uuid import UUID

def create_specification(db: Session, spec_in: SpecificationCreate) -> Specification:
    db_spec = Specification(**spec_in.dict())
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    return db_spec

def get_specifications(
    db: Session,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    file_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None
) -> List[Specification]:
    query = db.query(Specification)
    if status:
        query = query.filter(Specification.status == status)
    if assigned_to:
        query = query.filter(Specification.assigned_to == assigned_to)
    if uploaded_by:
        query = query.filter(Specification.uploaded_by == uploaded_by)
    if file_type:
        query = query.filter(Specification.mime_type == file_type)
    if date_from:
        query = query.filter(Specification.uploaded_on >= date_from)
    if date_to:
        query = query.filter(Specification.uploaded_on <= date_to)
    # Sorting
    if sort_by:
        sort_col = getattr(Specification, sort_by, None)
        if sort_col is not None:
            if sort_order and sort_order.lower() == 'asc':
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(Specification.uploaded_on.desc())
    return query.all()

def get_spec_by_file_path(db: Session, file_path: str) -> Specification:
    return db.query(Specification).filter(Specification.file_path == file_path).first() 