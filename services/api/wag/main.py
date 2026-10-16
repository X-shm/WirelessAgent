"""WirelessAgent - FastAPI entry point (projects / sessions / tasks slice)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from wag.config import settings
from wag.database import engine
from wag.limiter import limiter
from wag.middleware.auth import auth_middleware
from wag.models.base import Base
from wag.routes import auth, projects, session, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.middleware("http")(auth_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth.router, session.router, projects.router, tasks.router):
    app.include_router(router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}