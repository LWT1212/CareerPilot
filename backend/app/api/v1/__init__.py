# API v1模块
from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router

__all__ = ["auth_router", "projects_router"]
