"""
Health check endpoints for monitoring: load balancer checks, Docker/Kubernetes
readiness and liveness probes, and basic uptime monitoring.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


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
