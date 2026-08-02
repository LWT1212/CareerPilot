# CareerPilot AI 开发日志

## 项目信息

| 项目 | 内容 |
|------|------|
| **项目名称** | CareerPilot AI |
| **项目描述** | 基于Multi-Agent的长期项目成长助手 |
| **开始日期** | 2024-01-25 |
| **技术栈** | Vue3 + FastAPI + SQLite + ChromaDB |
| **仓库地址** | https://github.com/LWT1212/CareerPilot |

---

## 📋 步骤概览（快速查找用）

### Phase 0: 项目初始化 ✅
| Step | 操作 | 执行者 | 状态 |
|------|------|--------|------|
| 0.1 | 检查开发环境 | 用户 | ✅ |
| 0.2 | 创建GitHub仓库 | 用户 | ✅ |
| 0.3 | 更新 .gitignore | AI | ✅ |
| 0.4 | 配置Git用户信息 | 用户 | ✅ |
| 0.5 | 初始化Git仓库 | 用户 | ✅ |
| 0.6 | 添加远程仓库 | 用户 | ✅ |
| 0.7 | 添加文件并提交 | 用户 | ✅ |
| 0.8 | 推送到GitHub | 用户 | ✅ |
| 0.9 | 生成开发文档 | AI | ✅ |
| 0.10 | 提交文档到GitHub | 用户 | ✅ |

### Phase 1: 项目结构搭建 🟡
| Step | 操作 | 执行者 | 状态 |
|------|------|--------|------|
| 1.1 | 创建项目目录结构 | AI | ✅ |
| 1.2 | 创建后端入口文件 | AI | ✅ |
| 1.3 | 创建后端配置文件 | AI | ✅ |
| 1.4 | 创建requirements.txt | AI | ✅ |
| 1.5 | 创建数据库连接 | AI | ✅ |
| 1.6 | 创建Docker配置 | AI | ✅ |
| 1.7 | 创建前端项目 | AI | ⏳ |

### Phase 1: 用户系统（待开始）
| Step | 操作 | 执行者 | 状态 |
|------|------|--------|------|
| 1.1 | 后端FastAPI初始化 | AI | ⏳ |
| 1.2 | 数据库配置 | AI | ⏳ |
| 1.3 | 用户模型 | AI | ⏳ |
| 1.4 | 用户注册API | AI | ⏳ |
| 1.5 | 用户登录API | AI | ⏳ |
| 1.6 | JWT认证 | AI | ⏳ |
| 1.7 | 前端Vue3初始化 | AI | ⏳ |
| 1.8 | 登录页面 | AI | ⏳ |

### Phase 2: 项目管理（待开始）
| Step | 操作 | 状态 |
|------|------|------|
| 2.1 | 项目CRUD API | ⏳ |
| 2.2 | 前端项目列表页 | ⏳ |

### Phase 3: 聊天系统（待开始）
| Step | 操作 | 状态 |
|------|------|------|
| 3.1 | 聊天CRUD API | ⏳ |
| 3.2 | 消息流式响应 | ⏳ |
| 3.3 | 前端聊天界面 | ⏳ |

### Phase 4: 知识库RAG（待开始）
| Step | 操作 | 状态 |
|------|------|------|
| 4.1 | 文档上传API | ⏳ |
| 4.2 | 文档解析 | ⏳ |
| 4.3 | 向量嵌入 | ⏳ |
| 4.4 | RAG检索 | ⏳ |

### Phase 5: 经验管理（待开始）
### Phase 6: 面试模块（待开始）
### Phase 7: 文档管理（待开始）
### Phase 8: Multi-Agent系统（待开始）
### Phase 9-10: 测试与部署（待开始）

---

## 🐛 遇到的问题

| # | 问题 | 解决方案 | 状态 |
|---|------|----------|------|
| 1 | docker-compose命令不存在 | 使用 `docker compose` | ✅ |
| 2 | Git remote添加失败 | 重新添加并验证 | ✅ |

详细错误请查看 [ERRORS.md](ERRORS.md)

---

## 📋 技术决策

| # | 决策 | 选择 | 原因 |
|---|------|------|------|
| 1 | LLM选型 | OpenAI + Ollama | 灵活，生产用OpenAI，开发用Ollama |
| 2 | 数据库 | SQLite (V1) | 零配置，便于开发 |
| 3 | Git工作流 | GitHub Flow | 流程简单，适合小团队 |

---

## 📖 详细步骤

---

### [09:00] Step 0.1: 检查开发环境

**目标**: 确认必要的开发工具已安装

**执行命令**:
```bash
git --version
docker --version
docker compose version
node --version
python3 --version
```

**实际输出**:
```
git version 2.43.0
Docker version 29.5.2, build 79eb04c
Docker Compose version v5.1.4
v24.15.0
Python 3.12.7
```

**状态**: ✅ 成功

---

### [09:15] Step 0.2: 创建GitHub仓库

**目标**: 在GitHub上创建项目仓库

**操作步骤**:
1. 浏览器访问 https://github.com/new
2. Repository name: `CareerPilot`
3. Description: `基于Multi-Agent的长期项目成长助手`
4. **不要勾选**: Add README / Add .gitignore / Choose a license
5. 点击 Create repository

**实际结果**: 仓库创建成功 https://github.com/LWT1212/CareerPilot

**状态**: ✅ 成功

---

### [09:30] Step 0.3: 更新 .gitignore

**目标**: 配置Git忽略规则

**执行命令**:
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
venv/
.venv/

# Node
node_modules/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Database
*.db
*.sqlite3

# Uploads
uploads/

# Logs
*.log
EOF
```

**状态**: ✅ 成功

---

### [09:45] Step 0.4: 配置Git用户信息

**目标**: 设置Git提交时显示的用户名和邮箱

**执行命令**:
```bash
git config --global user.name "LWT1212"
git config --global user.email "15723669+LWT1212@users.noreply.github.com"
```

**验证命令**:
```bash
git config user.name
git config user.email
```

**状态**: ✅ 成功

---

### [10:00] Step 0.5: 初始化Git仓库

**目标**: 在本地创建Git仓库

**执行命令**:
```bash
cd ~/pyproject/Assistant
git init
```

**实际输出**:
```
Initialized empty Git repository in /home/magic/pyproject/Assistant/.git/
```

**状态**: ✅ 成功

---

### [10:05] Step 0.6: 添加远程仓库

**目标**: 将本地仓库与GitHub关联

**执行命令**:
```bash
git remote add origin https://github.com/LWT1212/CareerPilot.git
```

**验证命令**:
```bash
git remote -v
```

**实际输出**:
```
origin  https://github.com/LWT1212/CareerPilot.git (fetch)
origin  https://github.com/LWT1212/CareerPilot.git (push)
```

**状态**: ✅ 成功

---

### [10:10] Step 0.7: 添加文件并提交

**目标**: 将所有文件添加到Git并提交

**执行命令**:
```bash
git add .
git commit -m "feat: 初始化项目结构，添加开发前文档"
```

**实际输出**:
```
[main 64ef7b8] feat: 初始化项目结构，添加开发前文档
 15 files changed, 500 insertions(+)
```

**状态**: ✅ 成功

---

### [10:15] Step 0.8: 推送到GitHub

**目标**: 将代码推送到GitHub

**执行命令**:
```bash
git branch -M main
git push -u origin main
```

**实际输出**:
```
Enumerating objects: 15, done.
...
To https://github.com/LWT1212/CareerPilot.git
 * [new branch]      main -> main
```

**状态**: ✅ 成功

---

## Phase 1: 项目结构搭建

### [15:50] Step 1.1: 创建项目目录结构

**执行者**: AI助手
**目标**: 创建前后端目录结构

**执行命令**:
```bash
cd ~/pyproject/Assistant

# 创建后端目录结构
mkdir -p backend/app/{api/v1,models,schemas,services,agents,db,utils}
mkdir -p backend/tests

# 创建前端目录结构
mkdir -p frontend/src/{api,components,views,stores,router,utils,assets}
mkdir -p frontend/public

# 创建Docker配置目录
mkdir -p docker/nginx

# 创建上传目录
mkdir -p uploads
```

**实际输出**: 目录创建完成

**状态**: ✅ 成功

---

### [15:52] Step 1.2: 创建后端入口文件

**执行者**: AI助手
**目标**: 创建FastAPI主入口文件

**文件路径**: `backend/app/main.py`

**完整代码**:
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
    """健康检查接口"""
    return {"status": "healthy", "service": "CareerPilot AI"}

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "CareerPilot AI",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**状态**: ✅ 完成

---

### [15:53] Step 1.3: 创建后端配置文件

**执行者**: AI助手
**目标**: 创建应用配置文件

**文件路径**: `backend/app/config.py`

**完整代码**:
```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # App
    APP_NAME: str = "CareerPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./careerpilot.db"
    
    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
```

**状态**: ✅ 完成

---

### [15:54] Step 1.4: 创建requirements.txt

**执行者**: AI助手
**目标**: 定义Python依赖

**文件路径**: `backend/requirements.txt`

**完整内容**:
```
# FastAPI and ASGI
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.2

# LLM
openai==1.12.0
httpx==0.26.0

# Document Processing
unstructured==0.12.0
pypdf==3.17.1
python-docx==1.1.0

# Vector Database
chromadb==0.4.22

# Utilities
python-dotenv==1.0.0
aiofiles==23.2.1
```

**状态**: ✅ 完成

---

### [15:55] Step 1.5: 创建数据库连接

**执行者**: AI助手
**目标**: 创建SQLAlchemy数据库连接

**文件路径**: `backend/app/db/__init__.py`

**完整代码**:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
```

**状态**: ✅ 完成

---

### [15:56] Step 1.6: 创建Docker配置

**执行者**: AI助手
**目标**: 创建Docker相关配置文件

**文件1**: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**文件2**: `docker-compose.yml`

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
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    depends_on:
      - chromadb
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
    restart: unless-stopped

volumes:
  chroma_data:
```

**状态**: ✅ 完成

---

## 下一步

- Step 1.7: 创建前端项目
- 验证后端是否能启动

---

## Phase A: AI能力接入（2026-08-02）

### T1: LLM服务层 ✅
- 创建 `services/llm_service.py`：OpenAI/Ollama双引擎
- 通过 ChatOpenAI 统一封装（Ollama走/v1兼容接口）
- 修复 .env 路径（env_file=../.env）

### T2: 聊天接入LLM + SSE流式 ✅
- 非流式：chat_completion()
- 流式：SSE逐字输出（/stream接口）
- 前端 streamMessage() 解析SSE

### T3: 知识库RAG ✅
- 创建 `services/rag_service.py`
- 解析：TXT/MD/PDF/DOCX
- 分块：RecursiveCharacterTextSplitter(500/50)
- 嵌入：Ollama nomic-embed-text（768维）
- 存储：ChromaDB持久化（每项目一个集合）
- 检索：Top-K语义检索
- 项目聊天自动RAG增强
- 修复：numpy降级1.26.4（chromadb兼容）

### T4: LangGraph多智能体 ✅
- 创建 `agents/langgraph_workflow.py`
- Coordinator节点：LLM意图识别
- 条件路由：knowledge/experience/interview/document/chat
- 5个Agent节点各调用LLM
- Knowledge Agent集成RAG
- 聊天接口接入多智能体调度

### 遇到问题
| 问题 | 解决方案 |
|------|----------|
| OpenAI key为空 | .env路径改为../.env |
| Ollama 404 | base_url加/v1路径 |
| numpy 2.x与chromadb冲突 | 降级numpy<2 |
| chroma_data被提交 | 加入.gitignore |
