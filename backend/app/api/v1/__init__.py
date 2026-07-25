# API v1模块
from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.chats import router as chats_router, message_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.experiences import router as experiences_router

__all__ = ["auth_router", "projects_router", "chats_router", "message_router", "knowledge_router", "experiences_router"]
