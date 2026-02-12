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
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.router import api_router


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
    print("🚀 Starting AI Learning Platform Backend...")
    print(f"Environment : {settings.ENVIRONMENT}")
    print(f"LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    print(f"Model       : {settings.DEFAULT_LLM_MODEL}")

    yield

    # =========================
    # SHUTDOWN
    # =========================
    print("🛑 Shutting down backend...")


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
