"""
router.py
=========

Central API Router Aggregator.

Fungsi:
- Menggabungkan semua router endpoint
- Mengatur prefix versioning API
- Menjaga struktur routing tetap clean dan scalable

Current Scope:
✔ Chat Routes
✔ Health Routes

Future:
- Auth Routes
- Admin Routes
- Analytics Routes
"""

from fastapi import APIRouter

# Import V1 Routes
from api.v1.chat_routes import router as chat_router
from api.v1.health_routes import router as health_router


# =========================================================
# MAIN API ROUTER
# =========================================================
api_router = APIRouter()


# =========================================================
# API VERSIONING (v1)
# =========================================================
v1_router = APIRouter(prefix="/v1")


# Register V1 Routes
v1_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"],
)

v1_router.include_router(
    health_router,
    tags=["Health"],
)


# =========================================================
# REGISTER VERSION ROUTER KE MAIN API ROUTER
# =========================================================
api_router.include_router(v1_router)