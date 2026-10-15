"""Authentication middleware - extracts and verifies JWT from Authorization header."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from app.config import settings

PUBLIC_PATHS = {
    "/api/auth/guest",
    "/api/auth/login",
    "/api/auth/register",
    "/api/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}


async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if (
        path in PUBLIC_PATHS
        or path.startswith("/docs")
        or path.startswith("/openapi")
        or path.startswith("/redoc")
        or not path.startswith("/api/")
    ):
        return await call_next(request)

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