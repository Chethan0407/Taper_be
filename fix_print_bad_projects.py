from sqlalchemy import create_engine, text
from app.core.config import settings

# Get DB URL from settings
if settings.SQLALCHEMY_DATABASE_URI:
    db_url = settings.SQLALCHEMY_DATABASE_URI
else:
    db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, company_id FROM projects ORDER BY id;"))
    projects = result.fetchall()
    print("All projects:")
    for row in projects:
        print(row)
    if not projects:
        print("No projects found.") 