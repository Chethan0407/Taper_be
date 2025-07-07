from app.db.session import SessionLocal
from app.db.models import Project

db = SessionLocal()
try:
    deleted = db.query(Project).delete()
    db.commit()
    print(f"Deleted {deleted} projects from the database.")
finally:
    db.close() 