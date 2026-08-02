# CareerPilot AI - 服务器上线实战指南

> 基于本地生产部署实战经验编写。买好服务器后，照着本指南一步步操作即可上线。
> 最后更新: 2026-08-02（本地生产模式已跑通，本文是搬到云服务器的完整步骤）

---

## 一、部署架构

```
┌─────────────────────────────────────────────┐
│              Nginx (端口80/8080)             │
│  ├─ / → 前端静态文件 (frontend/dist)        │
│  └─ /api → 后端 FastAPI (gunicorn 4进程)    │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         Backend (Docker容器)                │
│   FastAPI + LangGraph + RAG + ChromaDB      │
│         (ChromaDB是嵌入式，无需单独容器)     │
└──────────────┬──────────────────────────────┘
               │ host.docker.internal:11434
               ▼
┌─────────────────────────────────────────────┐
│         Ollama (宿主机，qwen2.5)            │
└─────────────────────────────────────────────┘
```

**关键点**：
- 前端编译成静态文件，Nginx托管
- 后端跑在Docker容器（gunicorn多进程）
- ChromaDB用嵌入式模式（Python库直接跑在后端容器里，**不需要**单独的chromadb容器）
- Ollama跑在宿主机（因为模型大，不进容器）

---

## 二、服务器准备

### 2.1 购买服务器

推荐配置（最低）：
| 配置 | 要求 |
|------|------|
| 系统 | Ubuntu 22.04+ |
| CPU | 2核 |
| 内存 | 4GB+（跑7B模型建议8GB） |
| 磁盘 | 40GB+ |
| 带宽 | 3Mbps+ |

可选：阿里云 / 腾讯云 轻量应用服务器（约几十元/月）

### 2.2 SSH登录服务器

```bash
# 用你电脑的终端连接服务器
ssh root@你的服务器IP
# 或
ssh ubuntu@你的服务器IP
```

### 2.3 安装 Docker（服务器上执行）

```bash
# 一键安装Docker
curl -fsSL https://get.docker.com | sh

# 启动并开机自启
systemctl start docker
systemctl enable docker

# 验证
docker --version
docker compose version
```

### 2.4 配置 Docker 镜像加速（国内必做，否则拉镜像慢/失败）

```bash
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
  ]
}
EOF

# 重启Docker生效
systemctl restart docker
```

> ⚠️ 如果加速器失效，可搜索"docker镜像加速器"找新的可用地址。

---

## 三、安装 Ollama（宿主机）

### 3.1 安装

```bash
# 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型（二选一，或都拉）
ollama pull qwen2.5:3b      # 小模型，快，省内存
# ollama pull qwen2.5:7b    # 大模型，效果好，需要8G内存
# ollama pull nomic-embed-text  # 知识库向量模型（必须！RAG要用）
```

### 3.2 修改监听地址（关键！容器要访问它）

Ollama 默认只监听 127.0.0.1，容器访问不到。改成监听所有接口：

```bash
sudo systemctl edit ollama
```

在打开的编辑器中加入：
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

保存（`Ctrl+X` → `Y` → 回车），然后：

```bash
sudo systemctl restart ollama

# 验证：应显示 *:11434 而不是 127.0.0.1:11434
ss -tlnp | grep 11434
```

---

## 四、部署项目

### 4.1 克隆代码到服务器

```bash
cd /opt
git clone https://github.com/LWT1212/CareerPilot.git
cd CareerPilot
```

### 4.2 配置环境变量

```bash
cp .env.example .env
vim .env
```

确保 `.env` 中：
```
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

> 若用OpenAI/阿里云API，改为：
> ```
> LLM_PROVIDER=openai
> OPENAI_API_KEY=sk-你的真实key
> OPENAI_MODEL=qwen-plus
> ```

### 4.3 构建前端（本地构建后上传，或在服务器构建）

**方案A：本地构建好再上传（推荐）**
```bash
# 在你自己的电脑上
cd frontend && npm run build
# 把 frontend/dist 一起推到GitHub（或scp上传）
```

**方案B：服务器上构建**（需要Node.js）
```bash
# 服务器上
apt install -y nodejs npm
cd frontend && npm install && npm run build
```

> ⚠️ 服务器构建前端需要Node，且npm install可能较慢。推荐方案A。

### 4.4 构建并启动（服务器上）

```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### 4.5 验证

```bash
# 查看状态
docker compose -f docker-compose.prod.yml ps

# 健康检查
curl http://localhost:8080/health
# 应返回: {"status":"healthy","service":"CareerPilot AI"}

# 前端
curl http://localhost:8080/
# 应返回HTML
```

---

## 五、开放端口（让外网能访问）

### 5.1 云服务器安全组（控制台操作）

登录云厂商控制台 → 找到你的服务器 → 安全组/防火墙 → 添加入方向规则：

| 协议 | 端口 | 来源 | 用途 |
|------|------|------|------|
| TCP | 8080 | 0.0.0.0/0 | 应用访问 |
| TCP | 80 | 0.0.0.0/0 | HTTP（绑定域名时） |
| TCP | 443 | 0.0.0.0/0 | HTTPS（可选） |
| TCP | 22 | 你的IP | SSH（保持默认） |

### 5.2 服务器防火墙（如启用）

```bash
ufw allow 8080/tcp
ufw allow 80/tcp
ufw allow 443/tcp
```

### 5.3 验证外网访问

在你**自己的电脑**浏览器打开：
```
http://你的服务器IP:8080
```

能打开就上线成功了！

---

## 六、绑定域名 + HTTPS（可选但推荐）

### 6.1 购买域名并解析

1. 买域名（阿里云/腾讯云，约几十元/年）
2. 控制台 → DNS解析 → 添加记录：
   - 记录类型：A
   - 主机记录：www（或@）
   - 记录值：你的服务器IP

### 6.2 申请免费HTTPS证书（Let's Encrypt）

```bash
# 服务器上安装certbot
apt install -y certbot python3-certbot-nginx

# 获取证书（需要80端口已开放）
certbot certonly --standalone -d www.你的域名.com
```

### 6.3 修改Nginx配置启用HTTPS

编辑 `docker/nginx/default.conf`，添加：

```nginx
server {
    listen 443 ssl;
    server_name www.你的域名.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # 下面复制原来的 location 配置...
}
```

将证书复制到 `docker/nginx/ssl/` 目录，然后重启：
```bash
docker compose -f docker-compose.prod.yml restart nginx
```

### 6.4 完成

访问 `https://www.你的域名.com` —— HTTPS安全访问！

---

## 七、常见问题（实战踩坑记录）

### Q1: 前端能开，但API报502 Bad Gateway
**原因**：后端容器没起来（依赖缺失/启动失败）
**排查**：
```bash
docker logs assistant-backend-1
```
**解决**：根据日志修复后 `docker compose -f docker-compose.prod.yml up -d --force-recreate`

### Q2: 聊天回复"AI服务暂时不可用"
**原因1**：容器访问不到宿主机Ollama
**排查**：
```bash
# 容器内测试Ollama
docker exec assistant-backend-1 python3 -c "import urllib.request; print(urllib.request.urlopen('http://host.docker.internal:11434/api/tags',timeout=5).read()[:100])"
```
**解决1**：compose里加 `extra_hosts: ["host.docker.internal:host-gateway"]`（已配好）

**原因2**：Ollama只监听127.0.0.1
**解决2**：按"三、3.2"修改OLLAMA_HOST=0.0.0.0

**原因3**：没拉向量模型 nomic-embed-text（RAG报错）
**解决3**：`ollama pull nomic-embed-text`

### Q3: 构建很慢/卡住
**原因**：Docker Hub和pip官方源国内慢
**解决**：
- Docker镜像加速器（见2.4）
- requirements.txt已配清华源（pip config set）

### Q4: 构建报依赖冲突
**原因**：版本不兼容（曾遇到 pydantic、numpy 冲突）
**解决**：requirements.txt 已固定验证过的版本组合，不要随便升级

### Q5: /health 返回HTML而不是JSON
**原因**：Nginx把/health当前端路由处理了
**解决**：nginx配置里单独加 `location = /health` 代理后端（已配好）

### Q6: 端口80被占用
**原因**：服务器上已有其他服务占80
**解决**：compose里把 `8080:80` 改成其他端口，或停掉占用的服务

---

## 八、常用运维命令

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志（实时）
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx

# 重启某个服务
docker compose -f docker-compose.prod.yml restart backend

# 停止所有
docker compose -f docker-compose.prod.yml down

# 更新代码（git方式）
cd /opt/CareerPilot
git pull origin main
cd frontend && npm run build   # 如前端有改动
cd .. && docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# 备份数据库
cp backend/careerpilot.db backup_$(date +%Y%m%d).db

# 查看Ollama状态
ollama list
systemctl status ollama
```

---

## 九、数据持久化说明

| 数据 | 存储位置 | 说明 |
|------|----------|------|
| 用户/项目/聊天 | `backend/careerpilot.db` | SQLite数据库 |
| 上传文档 | `uploads/` | 上传的文件 |
| 向量数据 | `chroma_data/` | RAG向量索引 |
| LLM模型 | 宿主机Ollama目录 | 不进容器 |

> 升级代码前建议先备份数据库和uploads。
