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
| Step | 操作 | 状态 |
|------|------|------|
| 0.1 | 检查开发环境 | ✅ |
| 0.2 | 创建GitHub仓库 | ✅ |
| 0.3 | 更新 .gitignore | ✅ |
| 0.4 | 配置Git用户信息 | ✅ |
| 0.5 | 初始化Git仓库 | ✅ |
| 0.6 | 添加远程仓库 | ✅ |
| 0.7 | 添加文件并提交 | ✅ |
| 0.8 | 推送到GitHub | ✅ |

### Phase 1: 用户系统（待开始）
| Step | 操作 | 状态 |
|------|------|------|
| 1.1 | 创建项目结构 | ⏳ |
| 1.2 | 后端FastAPI初始化 | ⏳ |
| 1.3 | 用户注册API | ⏳ |
| 1.4 | 用户登录API | ⏳ |
| 1.5 | JWT认证 | ⏳ |

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

## 下一步

（待记录）
