# AI Mental Health Companion - API Module
# This file makes the api directory a Python package and provides router registration

from fastapi import APIRouter
from .chat import router as chat_router
from .mood import router as mood_router
from .coping import router as coping_router
from .users import router as users_router
from .dashboard import router as dashboard_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers with their prefixes
api_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    mood_router,
    prefix="/mood",
    tags=["mood"]
)

api_router.include_router(
    coping_router,
    prefix="/coping",
    tags=["coping"]
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["dashboard"]
)

__all__ = [
    "api_router",
    "chat_router",
    "mood_router",
    "coping_router",
    "users_router",
    "dashboard_router"
]
