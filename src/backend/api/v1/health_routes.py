"""
health_routes.py
================

Health check endpoints untuk monitoring service.

Digunakan untuk:
- Load balancer health check
- Docker container health check
- Kubernetes readiness / liveness probe
- Simple uptime monitoring

Scope saat ini:
✔ API Running Check
✔ Version Info
✔ Basic Status Info

Future:
- DB Health Check
- Redis Check
- LLM Provider Connectivity Check
"""

from datetime import datetime, timezone

from fastapi import APIRouter


router = APIRouter()


# =========================================================
# BASIC HEALTH CHECK
# =========================================================
@router.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint.

    Return:
    - status service
    - timestamp UTC
    """

    return {
        "status": "ok",
        "service": "chatbot-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =========================================================
# READINESS CHECK (Future: dependencies ready?)
# =========================================================
@router.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check.

    Digunakan oleh orchestrator untuk menentukan apakah service siap menerima traffic.
    """

    return {
        "status": "ready",
        "checks": {
            "api": True,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =========================================================
# LIVENESS CHECK (Future: process still alive?)
# =========================================================
@router.get("/health/live", tags=["Health"])
async def liveness_check():
    """
    Liveness check.

    Memastikan process tidak hang.
    """

    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
