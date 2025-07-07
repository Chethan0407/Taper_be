from sqlalchemy import create_engine, text
from app.core.config import settings

# Get DB URL from settings
if settings.SQLALCHEMY_DATABASE_URI:
    db_url = settings.SQLALCHEMY_DATABASE_URI
else:
    db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("DELETE FROM projects WHERE company_id IS NULL RETURNING id, name;"))
    deleted = result.fetchall()
    print(f"Deleted {len(deleted)} projects with company_id=NULL.")
    for row in deleted:
        print(row) 