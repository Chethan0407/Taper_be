import os
from app.db.session import SessionLocal
from app.crud.specification import get_spec_by_file_path, create_specification
from app.schemas.specification import SpecificationCreate

UPLOAD_DIR = "uploaded_specs"

def import_existing_specs():
    db = SessionLocal()
    for fname in os.listdir(UPLOAD_DIR):
        fpath = os.path.join(UPLOAD_DIR, fname)
        if os.path.isfile(fpath):
            if not get_spec_by_file_path(db, fpath):
                spec_in = SpecificationCreate(
                    file_name=fname,
                    mime_type="application/octet-stream",
                    uploaded_by="imported",
                    file_path=fpath
                )
                create_specification(db, spec_in)
    db.close() 