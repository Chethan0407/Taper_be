from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, companies, projects, specs, lint_results, comments, notifications, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(specs.router, prefix="/specs", tags=["specs"])
api_router.include_router(lint_results.router, prefix="/lint-results", tags=["lint-results"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"]) 