"""
FastAPI application entry point: creates the app, registers the API router,
configures CORS, and wires up the startup/shutdown lifespan.
"""

from contextlib import asynccontextmanager

from backend.api.router import api_router
from backend.core.config import settings
from backend.observability.logging.logger import get_logger
from backend.observability.logging.logging_config import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Logging must be configured before any other module creates a logger.
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown handler for app-level resources."""

    logger.info("Starting AI Learning Platform Backend")
    logger.info(f"Environment : {settings.ENVIRONMENT}")
    logger.info(f"LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    logger.info(f"Model       : {settings.DEFAULT_LLM_MODEL}")

    yield

    logger.info("🛑 Shutting down backend")


_is_production = settings.ENVIRONMENT == "production"

app = FastAPI(
    title="AI Learning Platform API",
    description="Backend API for AI Learning Platform Chatbot",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "AI Learning Platform Backend",
        "status": "running",
        "docs": app.docs_url,
    }
