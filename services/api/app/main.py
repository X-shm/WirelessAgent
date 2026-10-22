"""WirelessAgent 閳?FastAPI application entry point."""
import os
import sys
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.database import engine
from app.models.base import Base
from app.routes import auth, chat, session, file, rag, analytics, papers, projects, tasks
from app.middleware.auth import auth_middleware

# arXiv paper digest
os.environ.setdefault("ARXIV_DIGEST_DIR", settings.arxiv_digest_dir)
_DIGEST_SCRIPTS = os.path.join(settings.arxiv_digest_dir, "scripts")
if _DIGEST_SCRIPTS not in sys.path:
    sys.path.insert(0, _DIGEST_SCRIPTS)
from digest_routes import router as digest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (dev convenience; production uses Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Auth middleware (must be before CORS to process auth headers)
app.middleware("http")(auth_middleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(session.router)
app.include_router(file.router)
app.include_router(rag.router)
app.include_router(analytics.router)
app.include_router(papers.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(digest_router, prefix="/api/digest")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}

@app.get("/library", include_in_schema=False)
async def library_page():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "library.html"))



# 鈹€鈹€ Serve built frontend (production) 鈹€鈹€
_FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(_FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_FRONTEND_DIST, "assets")), name="static")
    @app.get("/{path:path}")
    async def spa_fallback(path: str):
        if path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404)
        index = os.path.join(_FRONTEND_DIST, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"detail": "Frontend not built"}

