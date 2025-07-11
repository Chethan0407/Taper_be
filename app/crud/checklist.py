from sqlalchemy.orm import Session
from app.db.models import Checklist
from app.schemas.checklist import ChecklistCreate
from typing import List

def create_checklist(db: Session, checklist_in: ChecklistCreate) -> Checklist:
    db_checklist = Checklist(**checklist_in.dict())
    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)
    return db_checklist

def get_checklists(db: Session) -> List[Checklist]:
    return db.query(Checklist).all() 