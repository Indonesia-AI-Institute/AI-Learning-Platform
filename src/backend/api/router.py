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
✔ Auth Routes
✔ Analytics Routes

Future:
- Course Routes
- Class Routes
- Task Routes
- Enrollment Routes
- Admin Routes
"""

from fastapi import APIRouter

# Import V1 Routes
from src.backend.api.v1.chat_routes import router as chat_router
from src.backend.api.v1.health_routes import router as health_router
from src.backend.api.v1.auth_routes import router as auth_router
from src.backend.api.v1.analytics_routes import router as analytics_router
from src.backend.api.v1.course_routes import router as course_router
from src.backend.api.v1.class_routes import router as class_router
from src.backend.api.v1.enrollment_routes import router as enrollment_router
from src.backend.api.v1.task_routes import router as task_router

# =========================================================
# MAIN API ROUTER
# =========================================================
api_router = APIRouter()


# =========================================================
# API VERSIONING (v1)
# =========================================================
v1_router = APIRouter(prefix="/v1")


# =========================================================
# REGISTER V1 ROUTES
# =========================================================
v1_router.include_router(
    chat_router,
    tags=["Chat"],
)

v1_router.include_router(
    health_router,
    tags=["Health"],
)

v1_router.include_router(
    auth_router,
    tags=["Auth"],
)

v1_router.include_router(
    course_router,
    tags=["Courses"]
)

v1_router.include_router(
    class_router,
    tags=["Classes"]
)

v1_router.include_router(
    task_router,
    tags=["Tasks"]
)

v1_router.include_router(
    enrollment_router,
    tags=["Enrollments"]
)

v1_router.include_router(
    analytics_router,
    tags=["Analytics"],
)

# =========================================================
# REGISTER VERSION ROUTER KE MAIN API ROUTER
# =========================================================
api_router.include_router(v1_router)