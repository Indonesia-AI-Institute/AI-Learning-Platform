"""
main.py
=======

FastAPI Application Entry Point.

Fungsi:
- Inisialisasi FastAPI app
- Register router API
- Setup middleware (CORS, dll)
- Setup lifespan event (startup / shutdown)

Scope Saat Ini:
✔ Chatbot API
✔ SSE Support
✔ REST Support
✔ Config based initialization

Future:
- DB connection init
- Redis init
- Vector DB init
- Telemetry
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.observability.logging.logging_config import setup_logging
from src.backend.observability.logging.logger import get_logger

from src.backend.core.config import settings
from src.backend.api.router import api_router



# =========================================================
# SETUP LOGGING (WAJIB PALING AWAL)
# =========================================================
setup_logging()
logger = get_logger(__name__)


# =========================================================
# LIFESPAN EVENT (Startup / Shutdown Handler)
# =========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler.

    Digunakan untuk:
    - Startup resource init
    - Shutdown cleanup
    """

    # =========================
    # STARTUP
    # =========================
    logger.info("Starting AI Learning Platform Backend")
    logger.info(f"Environment : {settings.ENVIRONMENT}")
    logger.info(f"LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    logger.info(f"Model       : {settings.DEFAULT_LLM_MODEL}")

    yield

    # =========================
    # SHUTDOWN
    # =========================
    logger.info("🛑 Shutting down backend")


# =========================================================
# CREATE FASTAPI APP
# =========================================================
app = FastAPI(
    title="AI Learning Platform API",
    description="Backend API for AI Learning Platform Chatbot",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# MIDDLEWARE - CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REGISTER API ROUTES
# =========================================================
app.include_router(api_router, prefix="/api")

# =========================================================
# ROOT ENDPOINT (Optional but useful)
# =========================================================
@app.get("/")
async def root():
    return {
        "service": "AI Learning Platform Backend",
        "status": "running",
        "docs": "/docs",
    }
