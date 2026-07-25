# 代码变更记录

> 记录所有重要的代码修改，包含完整代码，方便未来复制使用

---

## 2024-01-25: 项目初始化

### 1. .gitignore 文件

**文件路径**: `/.gitignore`

**完整代码**:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/
.eggs/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite3

# Uploads
uploads/

# Docker
docker-compose.override.yml

# Logs
*.log
logs/
```

**用途**: 配置Git忽略规则，避免提交不必要的文件

---

### 2. 创建目录结构

**执行命令**:
```bash
mkdir -p docs/journal/weekly
```

**创建的目录**:
```
docs/
└── journal/
    └── weekly/
```

---

### 3. 创建JOURNAL.md

**文件路径**: `docs/journal/JOURNAL.md`

**用途**: 主开发日志，按时间顺序记录所有操作

---

### 4. 创建ISSUES.md

**文件路径**: `docs/journal/ISSUES.md`

**用途**: 记录所有遇到的问题和解决方案

---

### 5. 创建DECISIONS.md

**文件路径**: `docs/journal/DECISIONS.md`

**用途**: 记录技术决策和原因

---

### 6. 创建COMMANDS.md

**文件路径**: `docs/journal/COMMANDS.md`

**用途**: 常用命令速查表

---

### 7. 创建PHASE0-GIT-SETUP.md

**文件路径**: `docs/journal/PHASE0-GIT-SETUP.md`

**用途**: Git初始化完整步骤（保姆级教程）

---

## 通用代码模板

### FastAPI 入口文件模板

**文件路径**: `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="CareerPilot AI",
    description="基于Multi-Agent的长期项目成长助手",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### FastAPI 配置文件模板

**文件路径**: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "CareerPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./careerpilot.db"
    
    # LLM
    LLM_PROVIDER: str = "openai"  # openai or ollama
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

### Docker Compose 开发环境模板

**文件路径**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    environment:
      - DATABASE_URL=sqlite:///./careerpilot.db
      - LLM_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - chromadb
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
    restart: unless-stopped

volumes:
  chroma_data:
```

---

### 后端 Dockerfile 模板

**文件路径**: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

### 前端 Vite 配置模板

**文件路径**: `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```
