# CareerPilot AI - 架构设计文档

| 项目 | 内容 |
|------|------|
| **架构风格** | 前后端分离 + Multi-Agent |
| **设计原则** | 模块化、可扩展、渐进式 |
| **最后更新** | 2024-01-20 |

---

## 一、系统架构图

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  用户层                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                      前端 (Vue3 + Vite)                         │     │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │     │
│    │  │   Chat   │  │ Knowledge│  │Experience│  │Interview │      │     │
│    │  │   页面   │  │   页面   │  │   页面   │  │   页面   │      │     │
│    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                  网络层                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                    Nginx (反向代理 + 静态资源)                    │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                  API层                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                   FastAPI (RESTful API)                         │     │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │     │
│    │  │   Auth   │  │ Projects │  │   Chat   │  │Knowledge │      │     │
│    │  │   API    │  │   API    │  │   API    │  │   API    │      │     │
│    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │     │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │     │
│    │  │Experience│  │Interview │  │Documents │                    │     │
│    │  │   API    │  │   API    │  │   API    │                    │     │
│    │  └──────────┘  └──────────┘  └──────────┘                    │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                  业务层                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                   Service Layer (业务逻辑)                       │     │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │     │
│    │  │   User   │  │ Project  │  │   Chat   │  │Knowledge │      │     │
│    │  │ Service  │  │ Service  │  │ Service  │  │ Service  │      │     │
│    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │     │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │     │
│    │  │Experience│  │Interview │  │Document  │                    │     │
│    │  │ Service  │  │ Service  │  │ Service  │                    │     │
│    │  └──────────┘  └──────────┘  └──────────┘                    │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                  Agent层                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                   Multi-Agent System                            │     │
│    │  ┌──────────────────────────────────────────────────────────┐  │     │
│    │  │              Coordinator Agent                           │  │     │
│    │  │              (统一调度 + 意图识别)                        │  │     │
│    │  └──────────────────────────────────────────────────────────┘  │     │
│    │         │              │              │              │         │     │
│    │         ▼              ▼              ▼              ▼         │     │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │     │
│    │  │Knowledge │  │Experience│  │Interview │  │Document  │     │     │
│    │  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │     │     │
│    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│                                    │                                        │
│                                    ▼                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                  数据层                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
│    │    SQLite     │  │   ChromaDB    │  │  File System  │               │
│    │   (关系数据)  │  │  (向量数据)   │  │  (文件存储)   │               │
│    └───────────────┘  └───────────────┘  └───────────────┘               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                  AI层                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌───────────────────────┐    ┌───────────────────────┐                 │
│    │     OpenAI API        │    │     Ollama (本地)     │                 │
│    │   (GPT-4 / GPT-3.5)  │    │     (Qwen / Llama)   │                 │
│    └───────────────────────┘    └───────────────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 1.2 数据流图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据流图                                        │
└─────────────────────────────────────────────────────────────────────────────┘

用户输入
    │
    ▼
┌─────────────┐
│   前端      │
│  (Vue3)     │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────┐
│   Nginx     │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│   Service   │────▶│   Agent     │
└─────────────┘     └─────────────┘     └──────┬──────┘
       │                                        │
       │                                        ▼
       │                                 ┌─────────────┐
       │                                 │    LLM      │
       │                                 │ (OpenAI/    │
       │                                 │  Ollama)    │
       │                                 └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Database  │     │   ChromaDB  │     │    Files    │
│  (SQLite)   │     │  (向量库)   │     │  (文档)     │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 二、模块划分

### 2.1 前端层

```
frontend/
├── src/
│   ├── api/                    # API 调用封装
│   │   ├── auth.ts             # 认证相关
│   │   ├── projects.ts         # 项目相关
│   │   ├── chats.ts            # 聊天相关
│   │   ├── knowledge.ts        # 知识库相关
│   │   ├── experiences.ts      # 经验相关
│   │   ├── interviews.ts       # 面试相关
│   │   └── documents.ts        # 文档相关
│   │
│   ├── components/             # 通用组件
│   │   ├── Layout/             # 布局组件
│   │   ├── Chat/               # 聊天组件
│   │   ├── Knowledge/          # 知识库组件
│   │   └── Common/             # 通用组件
│   │
│   ├── views/                  # 页面视图
│   │   ├── Login/              # 登录页
│   │   ├── Register/           # 注册页
│   │   ├── Home/               # 主页
│   │   ├── Projects/           # 项目管理
│   │   ├── Knowledge/          # 知识库
│   │   ├── Experiences/        # 经验库
│   │   ├── Interviews/         # 面试库
│   │   ├── Documents/          # 文档库
│   │   └── Settings/           # 设置
│   │
│   ├── stores/                 # Pinia 状态管理
│   │   ├── auth.ts             # 认证状态
│   │   ├── project.ts          # 项目状态
│   │   └── chat.ts             # 聊天状态
│   │
│   ├── router/                 # 路由配置
│   │   └── index.ts
│   │
│   └── utils/                  # 工具函数
│       ├── request.ts          # HTTP 请求
│       ├── auth.ts             # 认证工具
│       └── format.ts           # 格式化工具
```

---

### 2.2 API 层

```
backend/app/api/
├── v1/
│   ├── __init__.py
│   ├── router.py               # 路由汇总
│   │
│   ├── auth.py                 # 认证模块
│   │   ├── POST /register
│   │   ├── POST /login
│   │   ├── POST /refresh
│   │   ├── GET /me
│   │   ├── PUT /me
│   │   └── POST /change-pwd
│   │
│   ├── projects.py             # 项目模块
│   │   ├── GET /
│   │   ├── POST /
│   │   ├── GET /{id}
│   │   ├── PUT /{id}
│   │   └── DELETE /{id}
│   │
│   ├── chats.py                # 聊天模块
│   │   ├── GET /projects/{pid}/chats
│   │   ├── POST /projects/{pid}/chats
│   │   ├── GET /projects/{pid}/chats/{id}
│   │   ├── PUT /projects/{pid}/chats/{id}
│   │   └── DELETE /projects/{pid}/chats/{id}
│   │
│   ├── messages.py             # 消息模块
│   │   ├── GET /chats/{cid}/messages
│   │   └── POST /chats/{cid}/messages (SSE)
│   │
│   ├── knowledge.py            # 知识库模块
│   │   ├── GET /projects/{pid}/knowledge
│   │   ├── POST /projects/{pid}/knowledge
│   │   ├── GET /projects/{pid}/knowledge/{id}
│   │   ├── DELETE /projects/{pid}/knowledge/{id}
│   │   └── POST /projects/{pid}/knowledge/search
│   │
│   ├── experiences.py          # 经验模块
│   │   ├── GET /projects/{pid}/experiences
│   │   ├── POST /projects/{pid}/experiences
│   │   ├── GET /projects/{pid}/experiences/{id}
│   │   ├── PUT /projects/{pid}/experiences/{id}
│   │   └── DELETE /projects/{pid}/experiences/{id}
│   │
│   ├── interviews.py           # 面试模块
│   │   ├── GET /projects/{pid}/interviews
│   │   ├── POST /projects/{pid}/interviews
│   │   ├── GET /projects/{pid}/interviews/{id}
│   │   ├── PUT /projects/{pid}/interviews/{id}
│   │   ├── DELETE /projects/{pid}/interviews/{id}
│   │   ├── POST /interviews/{id}/questions
│   │   └── GET /projects/{pid}/interviews/stats
│   │
│   ├── documents.py            # 文档模块
│   │   ├── GET /projects/{pid}/documents
│   │   ├── GET /projects/{pid}/documents/{type}
│   │   ├── PUT /projects/{pid}/documents/{type}
│   │   └── POST /projects/{pid}/documents/{type}/generate
│   │
│   └── agents.py               # Agent模块
│       └── GET /agents/status
│
└── deps.py                     # 依赖注入
    ├── get_db
    ├── get_current_user
    └── get_llm_client
```

---

### 2.3 业务层

```
backend/app/services/
├── __init__.py
│
├── auth_service.py             # 认证服务
│   ├── register()
│   ├── login()
│   ├── refresh_token()
│   └── change_password()
│
├── project_service.py          # 项目服务
│   ├── create_project()
│   ├── get_projects()
│   ├── get_project()
│   ├── update_project()
│   └── delete_project()
│
├── chat_service.py             # 聊天服务
│   ├── create_chat()
│   ├── get_chats()
│   ├── get_chat()
│   ├── update_chat()
│   └── delete_chat()
│
├── message_service.py          # 消息服务
│   ├── get_messages()
│   ├── send_message()
│   └── stream_message()
│
├── knowledge_service.py        # 知识库服务
│   ├── upload_document()
│   ├── get_documents()
│   ├── get_document()
│   ├── delete_document()
│   ├── search_knowledge()
│   ├── parse_document()
│   ├── chunk_document()
│   └── embed_document()
│
├── experience_service.py       # 经验服务
│   ├── create_experience()
│   ├── get_experiences()
│   ├── get_experience()
│   ├── update_experience()
│   └── delete_experience()
│
├── interview_service.py        # 面试服务
│   ├── create_interview()
│   ├── get_interviews()
│   ├── get_interview()
│   ├── update_interview()
│   ├── delete_interview()
│   ├── add_question()
│   └── get_stats()
│
├── document_service.py         # 文档服务
│   ├── get_documents()
│   ├── get_document()
│   ├── update_document()
│   └── generate_document()
│
└── llm_service.py              # LLM服务
    ├── chat_completion()
    ├── stream_completion()
    ├── embed_text()
    └── get_client()
```

---

### 2.4 Agent 层

```
backend/app/agents/
├── __init__.py
│
├── base_agent.py               # Agent基类
│   ├── __init__()
│   ├── execute()
│   └── _parse_response()
│
├── coordinator_agent.py        # 调度Agent
│   ├── analyze_intent()        # 意图识别
│   ├── plan_tasks()            # 任务规划
│   └── dispatch_agents()       # 调度Agent
│
├── knowledge_agent.py          # 知识Agent
│   ├── search_knowledge()      # 知识检索
│   ├── answer_question()       # 技术问答
│   └── summarize_document()    # 文档总结
│
├── experience_agent.py         # 经验Agent
│   ├── organize_experience()   # 整理经验
│   ├── generate_growth_log()   # 生成成长记录
│   └── classify_issue()        # 问题分类
│
├── interview_agent.py          # 面试Agent
│   ├── analyze_interview()     # 分析面试
│   ├── identify_weakness()     # 识别薄弱点
│   ├── generate_suggestions()  # 生成建议
│   └── generate_timeline()     # 生成时间线
│
└── document_agent.py           # 文档Agent
    ├── generate_readme()       # 生成README
    ├── generate_prd()          # 生成PRD
    ├── generate_resume()       # 生成简历
    └── generate_star()         # 生成STAR描述
```

---

### 2.5 数据层

```
backend/app/
├── db/
│   ├── __init__.py
│   ├── session.py              # 数据库会话
│   ├── base.py                 # 模型基类
│   └── migrations/             # Alembic迁移
│       ├── env.py
│       ├── versions/
│       └── script.py.mako
│
├── models/                     # SQLAlchemy模型
│   ├── __init__.py
│   ├── user.py                 # 用户模型
│   ├── project.py              # 项目模型
│   ├── chat.py                 # 聊天模型
│   ├── message.py              # 消息模型
│   ├── knowledge.py            # 知识文档模型
│   ├── experience.py           # 经验模型
│   ├── interview.py            # 面试模型
│   ├── interview_question.py   # 面试问题模型
│   ├── document.py             # AI文档模型
│   ├── agent_execution.py      # Agent执行记录
│   └── user_setting.py         # 用户设置模型
│
└── schemas/                    # Pydantic模型
    ├── __init__.py
    ├── user.py                 # 用户Schema
    ├── project.py              # 项目Schema
    ├── chat.py                 # 聊天Schema
    ├── message.py              # 消息Schema
    ├── knowledge.py            # 知识Schema
    ├── experience.py           # 经验Schema
    ├── interview.py            # 面试Schema
    ├── document.py             # 文档Schema
    └── common.py               # 通用Schema
```

---

## 三、技术栈详细说明

### 3.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.x | 渐进式JavaScript框架 |
| Vite | 5.x | 下一代前端构建工具 |
| TypeScript | 5.x | JavaScript超集，类型安全 |
| Element Plus | 2.x | Vue3 UI组件库 |
| Pinia | 2.x | Vue3状态管理 |
| Vue Router | 4.x | 官方路由管理 |
| Axios | 1.x | HTTP客户端 |
| Tailwind CSS | 3.x | 原子化CSS框架（可选） |

**前端架构**：
- **组件化**：按功能模块划分组件
- **状态管理**：Pinia全局状态 + 组件局部状态
- **路由管理**：Vue Router，支持嵌套路由
- **API层**：Axios封装，统一错误处理

---

### 3.2 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.100+ | 高性能异步Web框架 |
| SQLAlchemy | 2.x | Python ORM |
| Pydantic | 2.x | 数据验证 |
| Alembic | 1.x | 数据库迁移 |
| uvicorn | 0.23+ | ASGI服务器 |
| python-jose | 3.x | JWT处理 |
| passlib | 1.x | 密码哈希 |
| python-multipart | 0.0.6+ | 文件上传 |

**后端架构**：
- **分层架构**：API → Service → Agent → Database
- **依赖注入**：FastAPI Depends
- **异步支持**：async/await
- **类型安全**：Pydantic模型验证

---

### 3.3 AI技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| OpenAI Python | 1.x | OpenAI API客户端 |
| LangChain | 0.1+ | LLM应用框架（可选） |
| ChromaDB | 0.4+ | 向量数据库 |
| Unstructured | 0.10+ | 文档解析 |
| PyPDF | 3.x | PDF解析 |
| python-docx | 1.x | Word解析 |

**AI架构**：
- **LLM双引擎**：OpenAI（云端）+ Ollama（本地）
- **RAG流程**：文档解析 → 分块 → 嵌入 → 检索 → 生成
- **Agent框架**：自实现 → LangGraph（V2）

---

### 3.4 基础设施

| 技术 | 版本 | 用途 |
|------|------|------|
| Docker | 24.x | 容器化 |
| Docker Compose | 2.x | 多容器编排 |
| Nginx | 1.25+ | 反向代理 |
| SQLite | 3.x | V1数据库 |
| PostgreSQL | 15+ | V2数据库 |
| Redis | 7+ | V2缓存 |

---

## 四、部署架构

### 4.1 开发环境

```
┌─────────────────────────────────────────────────────────────┐
│                     开发环境 (Docker Compose)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌────────────┐ │
│  │   Frontend    │    │   Backend     │    │   SQLite   │ │
│  │   (Vite Dev)  │    │   (Uvicorn)   │    │   (本地)   │ │
│  │   :5173       │    │   :8000       │    │            │ │
│  └───────────────┘    └───────────────┘    └────────────┘ │
│                                                             │
│  ┌───────────────┐    ┌───────────────┐                   │
│  │   ChromaDB    │    │   Ollama      │                   │
│  │   :8000       │    │   :11434      │                   │
│  └───────────────┘    └───────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 4.2 生产环境

```
┌─────────────────────────────────────────────────────────────┐
│                     生产环境 (Docker Compose)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Nginx                            │   │
│  │              :80 (HTTP) / :443 (HTTPS)              │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                    │                             │
│         ▼                    ▼                             │
│  ┌───────────────┐    ┌───────────────┐                   │
│  │   Frontend    │    │   Backend     │                   │
│  │   (静态文件)  │    │   (Uvicorn)   │                   │
│  │               │    │   :8000       │                   │
│  └───────────────┘    └───────────────┘                   │
│                            │                              │
│         ┌──────────────────┼──────────────────┐           │
│         ▼                  ▼                  ▼           │
│  ┌───────────────┐  ┌───────────────┐  ┌────────────┐   │
│  │  PostgreSQL   │  │    Redis      │  │  ChromaDB  │   │
│  │  :5432        │  │   :6379       │  │  :8000     │   │
│  └───────────────┘  └───────────────┘  └────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 4.3 Docker Compose 配置

```yaml
# docker-compose.yml (V1)
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
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

```yaml
# docker-compose.prod.yml (V2)
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx:/etc/nginx/conf.d
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/careerpilot
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
      - chromadb

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=careerpilot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  postgres_data:
  redis_data:
  chroma_data:
```

---

## 五、安全设计

### 5.1 认证安全

| 措施 | 说明 |
|------|------|
| JWT Token | 使用RS256算法签名 |
| Token有效期 | access_token 30分钟，refresh_token 7天 |
| 密码哈希 | 使用bcrypt算法 |
| CORS | 限制允许的域名 |

### 5.2 数据安全

| 措施 | 说明 |
|------|------|
| 输入验证 | Pydantic模型验证 |
| SQL注入防护 | SQLAlchemy ORM |
| XSS防护 | 前端转义 + CSP |
| 文件上传限制 | 限制文件类型和大小 |

### 5.3 API安全

| 措施 | 说明 |
|------|------|
| 速率限制 | 限制请求频率 |
| 错误处理 | 不暴露敏感信息 |
| 日志记录 | 记录关键操作 |
| HTTPS | 生产环境强制HTTPS |

---

## 六、性能设计

### 6.1 前端性能

| 优化 | 说明 |
|------|------|
| 代码分割 | 路由懒加载 |
| 资源压缩 | Gzip/Brotli |
| CDN加速 | 静态资源CDN |
| 缓存策略 | 浏览器缓存 |

### 6.2 后端性能

| 优化 | 说明 |
|------|------|
| 异步处理 | FastAPI异步 |
| 数据库索引 | 合理设计索引 |
| 连接池 | SQLAlchemy连接池 |
| 分页查询 | 避免大量数据加载 |

### 6.3 AI性能

| 优化 | 说明 |
|------|------|
| 流式响应 | SSE流式输出 |
| 向量检索 | ChromaDB高效检索 |
| 模型选择 | 小模型处理简单任务 |
| 缓存 | LLM响应缓存（V2） |

---

## 七、可扩展性设计

### 7.1 模块化设计

- 各模块独立，通过接口通信
- 新增模块不影响现有功能
- 支持按需加载

### 7.2 Agent扩展

- Agent基类统一接口
- 新增Agent只需继承基类
- 支持动态注册Agent

### 7.3 LLM扩展

- 支持多种LLM提供商
- 通过配置切换
- 支持自定义Base URL

### 7.4 数据库扩展

- V1: SQLite（简单）
- V2: PostgreSQL（生产）
- 通过配置切换

---

## 八、监控与日志

### 8.1 日志设计

```python
# 日志配置
LOGGING = {
    "version": 1,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "file": {"class": "logging.FileHandler", "filename": "app.log"},
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}
```

### 8.2 监控指标

| 指标 | 说明 |
|------|------|
| 请求量 | API请求次数 |
| 响应时间 | API响应时间 |
| 错误率 | 错误请求比例 |
| LLM调用 | LLM调用次数和耗时 |
| Agent执行 | Agent执行次数和耗时 |

---

## 九、未来演进

### 9.1 V2架构升级

```
V1 (当前)                    V2 (未来)
─────────────                ─────────────
SQLite                 →     PostgreSQL
单Agent执行            →     多Agent并行
自实现Agent            →     LangGraph
无缓存                 →     Redis缓存
基础监控               →     Prometheus + Grafana
```

### 9.2 功能扩展

| 阶段 | 功能 |
|------|------|
| V1.1 | GitHub Agent、Task Agent |
| V1.2 | Research Agent、Resume Agent |
| V2.0 | Web Search Agent、MCP工具 |
| V2.1 | 多用户、团队协作 |
| V2.2 | 插件系统 |
