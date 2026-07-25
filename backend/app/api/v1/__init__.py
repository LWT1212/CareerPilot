# API v1模块 - 导入所有路由
from app.api.v1.auth import router as auth_router

__all__ = ["auth_router"]
