# Gamma (TapeOutOps) Backend

A scalable backend service for semiconductor AI linting, spec management, and collaboration.

## Features

- User Authentication & Authorization
- Project & Company Management
- Spec File Upload & Versioning
- AI Lint Processing
- Comments & Collaboration
- Notifications & Integrations
- Reporting & Analytics

## Tech Stack

- FastAPI (Python)
- PostgreSQL
- Redis
- AWS S3
- Celery
- Docker & Kubernetes

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

## Development

- API documentation available at `/docs` when server is running
- Run tests with `pytest`
- Format code with `black`
- Lint code with `flake8`

## Project Structure

```
app/
├── api/            # API routes
├── core/           # Core functionality
├── db/             # Database models and migrations
├── services/       # Business logic
├── schemas/        # Pydantic models
└── utils/          # Utility functions
```

## License

Proprietary - All rights reserved 