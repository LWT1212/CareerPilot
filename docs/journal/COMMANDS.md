# 常用命令速查

## Git 命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `git --version` | 查看Git版本 | `git --version` |
| `git init` | 初始化仓库 | `git init` |
| `git remote add origin URL` | 添加远程仓库 | `git remote add origin https://github.com/...` |
| `git remote -v` | 查看远程仓库 | `git remote -v` |
| `git remote remove origin` | 删除远程仓库 | `git remote remove origin` |
| `git config --global user.name "name"` | 设置用户名 | `git config --global user.name "LWT1212"` |
| `git config --global user.email "email"` | 设置邮箱 | `git config --global user.email "xxx@xxx.com"` |
| `git add .` | 添加所有文件 | `git add .` |
| `git status` | 查看状态 | `git status` |
| `git commit -m "msg"` | 提交 | `git commit -m "feat: xxx"` |
| `git branch -M main` | 重命名分支 | `git branch -M main` |
| `git push -u origin main` | 推送 | `git push -u origin main` |
| `git pull origin main` | 拉取 | `git pull origin main` |
| `git log --oneline` | 查看日志 | `git log --oneline` |

---

## Docker 命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `docker --version` | 查看Docker版本 | `docker --version` |
| `docker compose version` | 查看Compose版本 | `docker compose version` |
| `docker compose up -d` | 启动服务（后台） | `docker compose up -d` |
| `docker compose down` | 停止服务 | `docker compose down` |
| `docker compose ps` | 查看服务状态 | `docker compose ps` |
| `docker compose logs -f` | 查看日志（实时） | `docker compose logs -f` |
| `docker compose logs -f backend` | 查看特定服务日志 | `docker compose logs -f backend` |
| `docker compose restart` | 重启服务 | `docker compose restart` |
| `docker compose build --no-cache` | 重新构建镜像 | `docker compose build --no-cache` |
| `docker compose exec backend bash` | 进入容器 | `docker compose exec backend bash` |

---

## Node.js 命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `node --version` | 查看Node版本 | `node --version` |
| `npm --version` | 查看npm版本 | `npm --version` |
| `npm init -y` | 初始化package.json | `npm init -y` |
| `npm install <pkg>` | 安装依赖 | `npm install vue` |
| `npm run dev` | 启动开发服务器 | `npm run dev` |
| `npm run build` | 构建生产版本 | `npm run build` |

---

## Python 命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `python3 --version` | 查看Python版本 | `python3 --version` |
| `pip install <pkg>` | 安装包 | `pip install fastapi` |
| `pip freeze > requirements.txt` | 导出依赖 | `pip freeze > requirements.txt` |
| `pip install -r requirements.txt` | 安装依赖 | `pip install -r requirements.txt` |
| `python3 -m venv venv` | 创建虚拟环境 | `python3 -m venv venv` |
| `source venv/bin/activate` | 激活虚拟环境 | `source venv/bin/activate` |

---

## 文件操作命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `ls -la` | 列出所有文件 | `ls -la` |
| `cd <dir>` | 进入目录 | `cd ~/pyproject` |
| `pwd` | 显示当前路径 | `pwd` |
| `mkdir -p <dir>` | 创建目录 | `mkdir -p docs/journal` |
| `touch <file>` | 创建文件 | `touch README.md` |
| `cat <file>` | 查看文件 | `cat .gitignore` |
| `cat > <file> << 'EOF'` | 写入文件 | 见下方示例 |

### 写入文件示例
```bash
cat > .gitignore << 'EOF'
# 内容
__pycache__/
*.py[cod]
EOF
```
