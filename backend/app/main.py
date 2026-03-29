"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis

from app.core.config import get_settings
from app.api.routes import auth, companies, campaigns, emails, analytics, insights, sponsors

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # Startup: verify Redis connectivity
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        print("✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")

    yield

    # Shutdown
    print("🔻 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:80",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(campaigns.router)
app.include_router(emails.router)
app.include_router(analytics.router)
app.include_router(analytics.tracking_router)
app.include_router(insights.router)
app.include_router(sponsors.router)


@app.get("/health")
async def health_check():
    """Health check endpoint — verifies DB and Redis connectivity."""
    health = {"status": "ok", "services": {}}

    # Check DB
    try:
        from app.core.database import engine
        from sqlalchemy import text

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health["services"]["database"] = "connected"
    except Exception as e:
        health["services"]["database"] = f"error: {str(e)}"
        health["status"] = "degraded"

    # Check Redis
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        health["services"]["redis"] = "connected"
    except Exception as e:
        health["services"]["redis"] = f"error: {str(e)}"
        health["status"] = "degraded"

    return health
