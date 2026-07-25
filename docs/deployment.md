# CareerPilot AI - 部署文档

| 项目 | 内容 |
|------|------|
| **部署方式** | Docker + Nginx |
| **环境** | 本地开发 / 生产环境 |
| **最后更新** | 2024-01-20 |

---

## 一、环境要求

### 1.1 开发环境

| 软件 | 版本 | 说明 |
|------|------|------|
| Docker | 24.0+ | 容器化运行环境 |
| Docker Compose | 2.20+ | 多容器编排 |
| Git | 2.40+ | 版本控制 |
| Node.js | 18.0+ | 前端开发（可选） |
| Python | 3.11+ | 后端开发（可选） |

### 1.2 生产环境

| 软件 | 版本 | 说明 |
|------|------|------|
| 服务器 | Ubuntu 22.04+ | 推荐2核4G以上 |
| Docker | 24.0+ | 容器化运行环境 |
| Docker Compose | 2.20+ | 多容器编排 |
| Nginx | 1.25+ | 反向代理 |
| 域名 | - | 可选，用于HTTPS |
| SSL证书 | - | 可选，用于HTTPS |

---

## 二、本地开发环境

### 2.1 克隆项目

```bash
# 克隆仓库
git clone https://github.com/your-username/CareerPilot.git
cd CareerPilot

# 切换到开发分支
git checkout develop
```

### 2.2 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑环境变量
vim .env
```

**.env 文件内容**：

```bash
# 数据库配置
DATABASE_URL=sqlite:///./careerpilot.db

# LLM配置（二选一）
# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4

# Ollama（本地）
# LLM_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=qwen

# ChromaDB配置
CHROMADB_URL=http://localhost:8000

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### 2.3 启动服务

```bash
# 使用Docker Compose启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2.4 访问应用

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端API | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |
| ChromaDB | http://localhost:8000 |

---

## 三、生产环境部署

### 3.1 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt install docker-compose-plugin -y

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 3.2 项目部署

```bash
# 克隆项目
git clone https://github.com/your-username/CareerPilot.git
cd CareerPilot

# 切换到main分支
git checkout main

# 配置环境变量
cp .env.example .env
vim .env
```

### 3.3 配置环境变量（生产）

```bash
# .env（生产环境）
# 数据库配置
DATABASE_URL=postgresql://postgres:password@db:5432/careerpilot

# LLM配置
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4

# ChromaDB配置
CHROMADB_URL=http://chromadb:8000

# JWT配置（使用随机生成的密钥）
JWT_SECRET_KEY=your-random-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Redis配置（V2）
REDIS_URL=redis://redis:6379

# 域名配置
DOMAIN=localhost
```

### 3.4 启动生产服务

```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 查看状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 四、Nginx 配置

### 4.1 开发环境Nginx

```nginx
# docker/nginx/default.conf
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE支持
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
    }

    # WebSocket支持（可选）
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4.2 生产环境Nginx（HTTPS）

```nginx
# docker/nginx/prod.conf
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL证书
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端API代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE支持
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

---

## 五、SSL证书配置

### 5.1 使用Let's Encrypt（免费）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 证书位置
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem

# 自动续期
sudo certbot renew --dry-run
```

### 5.2 复制证书到Docker

```bash
# 创建SSL目录
mkdir -p docker/nginx/ssl

# 复制证书
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/

# 设置权限
sudo chmod 600 docker/nginx/ssl/*.pem
```

---

## 六、数据库配置

### 6.1 SQLite（V1）

```bash
# SQLite配置（默认）
DATABASE_URL=sqlite:///./careerpilot.db
```

**优点**：
- 无需额外安装
- 配置简单
- 适合开发和小规模使用

**缺点**：
- 不支持并发写入
- 无用户权限管理

### 6.2 PostgreSQL（V2）

```bash
# PostgreSQL配置
DATABASE_URL=postgresql://postgres:password@db:5432/careerpilot
```

**docker-compose.prod.yml 配置**：

```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=careerpilot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
```

**优点**：
- 支持并发
- 功能强大
- 适合生产环境

---

## 七、向量数据库配置

### 7.1 ChromaDB

```yaml
services:
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - PERSIST_DIRECTORY=/chroma/chroma
    restart: unless-stopped

volumes:
  chroma_data:
```

**配置说明**：

| 配置 | 说明 |
|------|------|
| IS_PERSISTENT | 持久化存储 |
| PERSIST_DIRECTORY | 数据存储目录 |

---

## 八、Redis配置（V2）

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  redis_data:
```

**配置说明**：

| 配置 | 说明 |
|------|------|
| appendonly | 开启AOF持久化 |

---

## 九、Docker Compose 完整配置

### 9.1 开发环境

```yaml
# docker-compose.yml
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

### 9.2 生产环境

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/prod.conf:/etc/nginx/conf.d/default.conf
      - ./frontend/dist:/usr/share/nginx/html
      - ./docker/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/careerpilot
      - LLM_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - CHROMADB_URL=http://chromadb:8000
    depends_on:
      - db
      - redis
      - chromadb
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=careerpilot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  chroma_data:
```

---

## 十、常用命令

### 10.1 Docker Compose 命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend

# 重启服务
docker-compose restart

# 重建镜像
docker-compose build --no-cache

# 进入容器
docker-compose exec backend bash
```

### 10.2 数据库命令

```bash
# SQLite
sqlite3 careerpilot.db

# PostgreSQL
docker-compose exec db psql -U postgres -d careerpilot

# 运行迁移
docker-compose exec backend alembic upgrade head

# 创建迁移
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### 10.3 调试命令

```bash
# 查看容器日志
docker logs <container_id>

# 查看容器资源使用
docker stats

# 进入容器调试
docker exec -it <container_id> bash

# 查看网络
docker network ls
docker network inspect <network_name>
```

---

## 十一、监控与日志

### 11.1 日志配置

```python
# backend/app/config.py
import logging

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default"
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO"
    }
}
```

### 11.2 健康检查

```python
# backend/app/api/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/health/db")
async def db_health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

### 11.3 Docker健康检查

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 十二、备份与恢复

### 12.1 数据库备份

```bash
# SQLite备份
cp careerpilot.db careerpilot.backup.$(date +%Y%m%d).db

# PostgreSQL备份
docker-compose exec db pg_dump -U postgres careerpilot > backup_$(date +%Y%m%d).sql
```

### 12.2 数据库恢复

```bash
# SQLite恢复
cp careerpilot.backup.20240120.db careerpilot.db

# PostgreSQL恢复
cat backup_20240120.sql | docker-compose exec -T db psql -U postgres careerpilot
```

### 12.3 文件备份

```bash
# 备份上传文件
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

---

## 十三、常见问题

### 13.1 端口冲突

```bash
# 查看端口占用
lsof -i :8000
lsof -i :5432

# 修改docker-compose.yml中的端口映射
ports:
  - "8001:8000"  # 使用8001端口
```

### 13.2 数据库连接失败

```bash
# 检查数据库容器状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 检查环境变量
echo $DATABASE_URL
```

### 13.3 文件权限问题

```bash
# 修改上传目录权限
chmod -R 755 uploads/

# 修改Docker卷权限
sudo chown -R 1000:1000 uploads/
```

### 13.4 内存不足

```bash
# 查看容器资源使用
docker stats

# 限制容器内存
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 十四、CI/CD配置

### 14.1 GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_KEY }}
          script: |
            cd /path/to/CareerPilot
            git pull origin main
            docker-compose -f docker-compose.prod.yml build
            docker-compose -f docker-compose.prod.yml up -d
```

### 14.2 自动部署流程

```
Push to main
    ↓
GitHub Actions触发
    ↓
SSH到服务器
    ↓
拉取最新代码
    ↓
构建Docker镜像
    ↓
重启服务
    ↓
健康检查
```

---

## 十五、安全配置

### 15.1 环境变量安全

```bash
# 不要将.env提交到Git
echo ".env" >> .gitignore

# 使用.env.example作为示例
cp .env.example .env
```

### 15.2 Docker安全

```yaml
services:
  backend:
    # 不以root运行
    user: "1000:1000"
    
    # 只读文件系统
    read_only: true
    
    # 临时目录
    tmpfs:
      - /tmp
```

### 15.3 Nginx安全

```nginx
# 安全头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'" always;

# 限制请求大小
client_max_body_size 10M;
```
