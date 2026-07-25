# CareerPilot AI 开发日志

## 项目信息

| 项目 | 内容 |
|------|------|
| **项目名称** | CareerPilot AI |
| **项目描述** | 基于Multi-Agent的长期项目成长助手 |
| **开始日期** | 2024-01-25 |
| **技术栈** | Vue3 + FastAPI + SQLite + ChromaDB |
| **仓库地址** | https://github.com/LWT1212/CareerPilot |
| **本地路径** | ~/pyproject/Assistant |

---

## Phase 0: 项目初始化

**状态**: ✅ 完成

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

## 遇到的问题

---

### 🐛 Issue #1: docker-compose 命令不存在

**时间**: 09:05
**步骤**: Step 0.1
**状态**: 🟢 已解决

**错误命令**:
```bash
docker-compose --version
```

**错误输出**:
```
bash: docker-compose: command not found
```

**问题原因**: Docker 29.x 已内置 docker compose，不需要单独安装

**解决方案**:
```bash
docker compose version
```

**经验**: 新版本软件可能改变命令行接口

---

### 🐛 Issue #2: Git remote 添加失败

**时间**: 10:20
**步骤**: Step 0.8
**状态**: 🟢 已解决

**错误命令**:
```bash
git push -u origin main
```

**错误输出**:
```
fatal: 'origin' does not appear to be a git repository
fatal: Could not read from remote repository.
```

**问题原因**: 远程仓库地址未正确添加

**解决方案**:
```bash
git remote remove origin 2>/dev/null
git remote add origin https://github.com/LWT1212/CareerPilot.git
git remote -v  # 验证
```

**经验**: 添加远程仓库后，用 `git remote -v` 验证

---

## 技术决策

---

### 📋 Decision #1: LLM 选型

**时间**: 09:00
**背景**: 需要确定V1阶段使用哪个LLM

**最终决定**: 同时支持 OpenAI 和 Ollama

**原因**: 
- OpenAI效果好，适合生产
- Ollama免费，适合开发和隐私场景
- 通过配置切换

---

### 📋 Decision #2: 数据库选型

**时间**: 09:00

**最终决定**: V1使用SQLite，V2迁移到PostgreSQL

**原因**: SQLite零配置，便于快速开发

---

### 📋 Decision #3: Git工作流

**时间**: 09:00

**最终决定**: 使用 GitHub Flow

**流程**: main → develop → feature/* → PR → Merge

---

## 下一步

### Phase 0 剩余任务
- [ ] 配置项目结构（前后端目录）
- [ ] Docker环境搭建
- [ ] 数据库初始化

### Phase 1: 用户系统（待开始）
- [ ] 后端FastAPI项目初始化
- [ ] 用户注册/登录API
- [ ] JWT认证
- [ ] 前端登录页面
