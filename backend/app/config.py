from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """应用配置"""

    # 应用基本信息
    APP_NAME: str = "CareerPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./careerpilot.db"

    # LLM配置（二选一）
    LLM_PROVIDER: str = "openai"  # openai 或 ollama
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_BASE_URL: str = ""  # 自定义OpenAI兼容端点（阿里云DashScope等）
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen"

    # JWT认证配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # CORS配置（允许前端访问）
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Redis 配置（LLM响应缓存）
    REDIS_URL: str = "redis://localhost:6379/0"
    LLM_CACHE_TTL: int = 3600  # 缓存有效期（秒），默认1小时

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        # .env 在项目根目录（backend/ 的上一级）
        env_file = "../.env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
