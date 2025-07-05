from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger, configure_logging
from app.core.rate_limit import limiter
from app.api.v1.api import api_router
from app.middleware.logging import RequestLoggingMiddleware
# from app.middleware.rate_limit import RateLimitMiddleware

# Setup structured logging
setup_logging()
logger = get_logger(__name__)

# Configure logging
configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add middlewares
app.add_middleware(RequestLoggingMiddleware)
# app.add_middleware(RateLimitMiddleware, rate_limit="1000/minute")

# Always add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(
        "request_started",
        method=request.method,
        url=str(request.url),
        client_host=request.client.host if request.client else None
    )
    
    response = await call_next(request)
    
    logger.info(
        "request_completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code
    )
    
    return response 