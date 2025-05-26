import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.v1 import api_router
from app.config import settings
from app.core import get_password_hash
from app.database import engine, Base, AsyncSessionLocal
from app.models import User



@asynccontextmanager
async def life_span(app: FastAPI):
    """Life-Span context manager for startup and shutdown events"""
    # === Startup ===
    # === Create upload dir ===
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # === Create tables ===
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # === Create first superuser to escape manual ===
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        )
        user = result.scalar_one_or_none()


        if not user:
            user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username='mukhsin_mukhtariy',
                full_name='Mukhsin Mukhtorov',
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_active=True,
                is_superuser=True,
            )
            db.add(user)
            await db.commit()

    yield

    # == Shut down the engine ===
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=life_span,
)

# === Add CORS middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# == Include API router ===
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to BookStore API, Glad to see you Mukhsin!",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "I am feeling awesome Mukhsin!!!! Running like a Senior developer coded me!)"}

