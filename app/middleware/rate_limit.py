from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

# Create a limiter instance with Redis backend
redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
limiter = Limiter(key_func=get_remote_address, storage_uri=redis_url)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: str = "1000/minute"):
        super().__init__(app)
        self.rate_limit = rate_limit

    async def dispatch(self, request: Request, call_next):
        try:
            # Apply rate limiting
            limiter.check_rate_limit(request, self.rate_limit)
            return await call_next(request)
        except Exception as e:
            logger.warning(
                "rate_limit_exceeded",
                client_ip=request.client.host if request.client else None,
                path=request.url.path,
                method=request.method
            )
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            ) 