import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger, log_request, log_error

logger = get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            log_request(
                logger=logger,
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration,
                client_host=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
            
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_error(
                logger=logger,
                request_id=request_id,
                error=e,
                method=request.method,
                path=request.url.path,
                duration_ms=duration
            )
            raise 