from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings

class AllowedHostsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "").split(":")[0]
        
        if host not in settings.ALLOWED_HOSTS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Host not allowed"
            )
        
        response = await call_next(request)
        return response