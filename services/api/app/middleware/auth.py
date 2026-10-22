"""Authentication middleware 鈥?extracts and verifies JWT from Authorization header."""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.config import settings
from jose import jwt, JWTError

# Paths that don't require authentication
PUBLIC_PATHS = {"/api/auth/guest", "/api/auth/login", "/api/auth/register", "/api/health", "/docs", "/openapi.json", "/redoc"}


async def auth_middleware(request: Request, call_next):
    # Allow public paths
    if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/api/digest") or not request.url.path.startswith("/api/") or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
        return await call_next(request)

    # Allow OPTIONS (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Missing or invalid token"})

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        request.state.user_id = payload.get("sub")
        request.state.user_email = payload.get("email")
    except JWTError:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Token is invalid or expired"})

    return await call_next(request)
