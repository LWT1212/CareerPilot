# 参考资料

> 常用命令、代码模板、详细教程

---

## 一、常用命令速查

### Git 命令

| 命令 | 用途 |
|------|------|
| `git --version` | 查看版本 |
| `git init` | 初始化仓库 |
| `git remote add origin URL` | 添加远程仓库 |
| `git remote -v` | 查看远程仓库 |
| `git remote remove origin` | 删除远程仓库 |
| `git config --global user.name "name"` | 设置用户名 |
| `git config --global user.email "email"` | 设置邮箱 |
| `git add .` | 添加所有文件 |
| `git status` | 查看状态 |
| `git commit -m "msg"` | 提交 |
| `git branch -M main` | 重命名分支 |
| `git push -u origin main` | 推送 |
| `git pull origin main` | 拉取 |
| `git log --oneline` | 查看日志 |

### Docker 命令

| 命令 | 用途 |
|------|------|
| `docker --version` | 查看版本 |
| `docker compose version` | 查看Compose版本 |
| `docker compose up -d` | 启动服务 |
| `docker compose down` | 停止服务 |
| `docker compose ps` | 查看状态 |
| `docker compose logs -f` | 查看日志 |
| `docker compose restart` | 重启服务 |
| `docker compose exec backend bash` | 进入容器 |

### Node.js 命令

| 命令 | 用途 |
|------|------|
| `node --version` | 查看版本 |
| `npm init -y` | 初始化package.json |
| `npm install <pkg>` | 安装依赖 |
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 |

### Python 命令

| 命令 | 用途 |
|------|------|
| `python3 --version` | 查看版本 |
| `pip install <pkg>` | 安装包 |
| `pip freeze > requirements.txt` | 导出依赖 |
| `python3 -m venv venv` | 创建虚拟环境 |
| `source venv/bin/activate` | 激活虚拟环境 |

---

## 二、Git 初始化完整步骤

### Step 1: 创建GitHub仓库

1. 打开 https://github.com/new
2. 填写仓库名称: `CareerPilot`
3. **不要勾选**: Add README / .gitignore / License
4. 点击 Create repository

### Step 2: 配置Git

```bash
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"
```

### Step 3: 初始化本地仓库

```bash
cd ~/pyproject/Assistant
git init
```

### Step 4: 添加远程仓库

```bash
git remote add origin https://github.com/用户名/仓库名.git
git remote -v  # 验证
```

### Step 5: 提交代码

```bash
git add .
git commit -m "feat: 初始化项目"
```

### Step 6: 推送到GitHub

```bash
git branch -M main
git push -u origin main
```

### 常见问题

**remote already exists**:
```bash
git remote remove origin
git remote add origin URL
```

**push被拒绝**:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

---

## 三、代码模板

### FastAPI 入口文件

**文件**: `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CareerPilot AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

### FastAPI 配置文件

**文件**: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./careerpilot.db"
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Docker Compose

**文件**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=sqlite:///./careerpilot.db
    depends_on:
      - chromadb

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  chroma_data:
```

### 后端 Dockerfile

**文件**: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 前端 Vite 配置

**文件**: `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
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

### .gitignore 模板

```gitignore
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
```

---

## 四、数据库表结构

### users 表

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### projects 表

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 五、API 接口速查

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 注册 |
| POST | /api/v1/auth/login | 登录 |
| GET | /api/v1/auth/me | 获取当前用户 |
| GET | /api/v1/projects | 项目列表 |
| POST | /api/v1/projects | 创建项目 |
| GET | /api/v1/projects/{id} | 项目详情 |
| POST | /api/v1/chats/{id}/messages | 发送消息 |
| POST | /api/v1/knowledge/search | 知识检索 |
