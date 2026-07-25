# CareerPilot AI

基于 Multi-Agent 的长期项目成长助手（AI Project Growth Assistant）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)

---

## 简介

CareerPilot AI 是一款基于 Multi-Agent 的长期项目成长助手。产品以 **Project（项目）** 为核心对象，通过多个智能体协同工作，持续收集、整理、分析和优化整个项目生命周期中的知识、问题、经验以及面试反馈，帮助开发者形成完整的成长闭环。

### 核心特色

- **Multi-Agent 协同**：5个智能体各司其职，协同完成任务
- **长期项目管理**：以 Project 为核心，管理整个项目生命周期
- **知识库 RAG**：上传文档，自动解析、嵌入、检索
- **面试成长闭环**：记录面试过程，自动分析薄弱点，持续提升
- **AI 文档生成**：自动维护 README、PRD、简历等文档

---

## 功能特性

### 核心模块

| 模块 | 说明 |
|------|------|
| **Project** | 项目管理，一个项目对应一次长期开发 |
| **Chat** | ChatGPT 风格聊天界面，支持流式响应 |
| **Knowledge** | 知识库管理，支持 RAG 检索 |
| **Experience** | 开发经验沉淀，自动整理成长记录 |
| **Interview** | 面试成长，自动分析薄弱点和学习建议 |
| **Documents** | AI 文档生成，自动维护项目文档 |

### Multi-Agent 系统

| Agent | 职责 |
|-------|------|
| **Coordinator Agent** | 统一调度，理解用户意图，制定执行计划 |
| **Knowledge Agent** | RAG 检索，技术问答，文档总结 |
| **Experience Agent** | 开发经验整理，自动生成成长记录 |
| **Interview Agent** | 面试分析，成长轨迹，高频问题统计 |
| **Document Agent** | 文档自动生成，README、PRD、简历 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue3 + Vite + TypeScript + Element Plus + Pinia |
| **后端** | FastAPI + SQLAlchemy + Pydantic + Alembic |
| **数据库** | SQLite（V1）→ PostgreSQL（V2） |
| **向量数据库** | ChromaDB |
| **大模型** | OpenAI / Ollama（Qwen） |
| **部署** | Docker + Nginx |
| **CI/CD** | GitHub Actions |

---

## 快速开始

### 环境要求

- Docker 24.0+
- Docker Compose 2.20+
- Git 2.40+

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/CareerPilot.git
cd CareerPilot

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 LLM API Key 等

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
# 前端: http://localhost:5173
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 环境变量配置

```bash
# .env 文件内容

# LLM配置（二选一）
# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4

# Ollama（本地）
# LLM_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=qwen

# JWT配置
JWT_SECRET_KEY=your-secret-key
```

---

## 项目结构

```
CareerPilot/
├── .github/                  # GitHub Actions
├── backend/                  # 后端 FastAPI
│   ├── app/
│   │   ├── api/             # API路由
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic模型
│   │   ├── services/        # 业务逻辑
│   │   ├── agents/          # Multi-Agent
│   │   └── db/              # 数据库
│   ├── tests/               # 测试
│   └── alembic/             # 数据库迁移
├── frontend/                 # 前端 Vue3
│   ├── src/
│   │   ├── api/             # API调用
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # 状态管理
│   │   └── router/          # 路由
│   └── ...
├── docs/                     # 项目文档
├── docker/                   # Docker配置
├── docker-compose.yml        # Docker Compose
└── README.md                 # 项目说明
```

---

## 文档

| 文档 | 说明 |
|------|------|
| [PRD](docs/PRD.md) | 产品需求文档 |
| [数据库设计](docs/database-design.md) | 数据库表结构设计 |
| [API接口设计](docs/api-design.md) | RESTful API接口文档 |
| [架构设计](docs/architecture.md) | 系统架构设计 |
| [开发规范](docs/development-guide.md) | 开发规范和最佳实践 |
| [部署文档](docs/deployment.md) | 部署配置和操作指南 |

---

## 开发指南

### 本地开发

```bash
# 启动开发环境
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 代码规范

- Python: PEP 8 + Black格式化
- TypeScript: ESLint + Prettier
- Git: Conventional Commits

### 提交代码

```bash
# 创建功能分支
git checkout -b feature/your-feature

# 提交代码
git commit -m "feat(module): description"

# 推送并创建PR
git push origin feature/your-feature
```

---

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | POST /api/v1/auth/login | 用户登录 |
| 项目 | GET /api/v1/projects | 获取项目列表 |
| 聊天 | POST /api/v1/chats/{id}/messages | 发送消息 |
| 知识库 | POST /api/v1/knowledge/search | 知识检索 |
| 面试 | GET /api/v1/interviews/stats | 面试统计 |

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 遵循 [开发规范文档](docs/development-guide.md)
- 使用 Conventional Commits 规范
- 添加必要的测试
- 更新相关文档

---

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 联系方式

- 项目主页: https://github.com/your-username/CareerPilot
- Issues: https://github.com/your-username/CareerPilot/issues

---

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能异步Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue3 UI组件库
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [OpenAI](https://openai.com/) - GPT模型
