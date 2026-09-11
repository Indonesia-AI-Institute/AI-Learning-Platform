"""Central API router aggregator: combines all v1 routers and applies prefix versioning."""

from backend.api.v1.analytics_routes import router as analytics_router
from backend.api.v1.auth_routes import router as auth_router
from backend.api.v1.chat_routes import router as chat_router
from backend.api.v1.class_routes import router as class_router
from backend.api.v1.course_routes import router as course_router
from backend.api.v1.enrollment_routes import router as enrollment_router
from backend.api.v1.health_routes import router as health_router
from backend.api.v1.task_routes import router as task_router
from fastapi import APIRouter

api_router = APIRouter()

v1_router = APIRouter(prefix="/v1")

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

api_router.include_router(v1_router)