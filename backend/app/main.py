from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.auth import router as auth_router
from app.db import init_db

# 创建FastAPI应用
app = FastAPI(
    title="CareerPilot AI",
    description="基于Multi-Agent的长期项目成长助手",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")


# 启动时初始化数据库
@app.on_event("startup")
def startup():
    init_db()


# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CareerPilot AI"}


# 根路径
@app.get("/")
async def root():
    return {
        "name": "CareerPilot AI",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
