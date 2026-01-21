from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from helperFunction.jwt_helper import verify_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        public_paths = ["/", "/docs", "/redoc", "/openapi.json", "/favicon.ico", "/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/verify-email", "/api/v1/auth/logout", "/api/v1/auth/users/stats", "/api/v1/users/students", "/api/v1/users/teachers"]
        
        # Skip auth for upload endpoints, course creation, and payment endpoints
        if (request.url.path.startswith("/api/v1/upload/") or 
            request.url.path.startswith("/api/v1/courses/") or
            request.url.path.startswith("/api/v1/payment/")):
            response = await call_next(request)
            return response
        
        if request.url.path in public_paths:
            response = await call_next(request)
            return response
        
        # Check for authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing or invalid"
            )
        
        token = auth_header.split(" ")[1]
        try:
            payload = verify_token(token)
            request.state.user_id = payload.get("sub")
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        response = await call_next(request)
        return response