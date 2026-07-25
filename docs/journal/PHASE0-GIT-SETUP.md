# Phase 0: Git 初始化完整步骤

> 本文件记录了从零开始初始化Git仓库并推送到GitHub的完整步骤，每一步都有具体命令。

---

## 前置准备

### Step 0: 确认当前目录

**目标**: 确认你在正确的项目目录

**执行命令**:
```bash
# 显示当前目录路径
pwd

# 列出当前目录内容
ls -la
```

**预期输出**:
```
/home/magic/pyproject/Assistant
```

---

## 第一部分：创建GitHub仓库

### Step 1: 打开GitHub创建页面

**目标**: 在浏览器中创建新的GitHub仓库

**操作步骤**:
1. 打开浏览器
2. 访问网址: https://github.com/new
3. 登录你的GitHub账号（如果还没登录）

---

### Step 2: 填写仓库信息

**目标**: 填写新仓库的基本信息

**填写内容**:

| 字段 | 填写内容 | 说明 |
|------|----------|------|
| Repository name | `CareerPilot` | 仓库名称 |
| Description | `基于Multi-Agent的长期项目成长助手` | 仓库描述 |
| Visibility | Public 或 Private | 选择公开或私有 |

**重要**: 以下选项 **不要勾选**:
- ❌ Add a README file
- ❌ Add .gitignore
- ❌ Choose a license

**原因**: 我们本地已经有这些文件了，勾选会导致冲突

---

### Step 3: 点击创建

**目标**: 完成仓库创建

**操作步骤**:
1. 检查填写信息是否正确
2. 点击绿色按钮 **Create repository**

**预期结果**: 页面跳转到新仓库页面，显示仓库地址

**记录你的仓库地址**:
```
你的仓库地址: https://github.com/LWT1212/CareerPilot.git
```

---

## 第二部分：配置Git用户信息

### Step 4: 配置用户名

**目标**: 设置Git提交时显示的用户名

**执行命令**:
```bash
git config --global user.name "你的GitHub用户名"
```

**示例**:
```bash
git config --global user.name "LWT1212"
```

**验证命令**:
```bash
git config --global user.name
```

**预期输出**:
```
LWT1212
```

---

### Step 5: 配置邮箱

**目标**: 设置Git提交时显示的邮箱

**执行命令**:
```bash
git config --global user.email "你的GitHub邮箱@example.com"
```

**示例**:
```bash
git config --global user.email "15723669+LWT1212@users.noreply.github.com"
```

**验证命令**:
```bash
git config --global user.email
```

**预期输出**:
```
15723669+LWT1212@users.noreply.github.com
```

---

## 第三部分：初始化本地Git仓库

### Step 6: 进入项目目录

**目标**: 切换到你的项目文件夹

**执行命令**:
```bash
cd ~/pyproject/Assistant
```

**验证命令**:
```bash
pwd
```

**预期输出**:
```
/home/magic/pyproject/Assistant
```

---

### Step 7: 初始化Git仓库

**目标**: 在当前目录创建Git仓库

**执行命令**:
```bash
git init
```

**预期输出**:
```
Initialized empty Git repository in /home/magic/pyproject/Assistant/.git/
```

**验证命令**:
```bash
ls -la .git
```

**预期输出**: 会显示.git目录的内容，说明初始化成功

---

### Step 8: 添加远程仓库

**目标**: 将本地仓库与GitHub远程仓库关联

**执行命令**:
```bash
git remote add origin https://github.com/LWT1212/CareerPilot.git
```

**注意**: 把 `LWT1212/CareerPilot` 替换成你自己的用户名/仓库名

---

### Step 9: 验证远程仓库

**目标**: 确认远程仓库添加成功

**执行命令**:
```bash
git remote -v
```

**预期输出**:
```
origin  https://github.com/LWT1212/CareerPilot.git (fetch)
origin  https://github.com/LWT1212/CareerPilot.git (push)
```

**如果输出为空或错误**, 执行以下命令重新添加:
```bash
git remote remove origin
git remote add origin https://github.com/LWT1212/CareerPilot.git
```

---

## 第四部分：添加文件并提交

### Step 10: 添加所有文件到暂存区

**目标**: 将项目文件添加到Git暂存区

**执行命令**:
```bash
git add .
```

**说明**: `.` 表示当前目录下的所有文件

---

### Step 11: 查看状态

**目标**: 确认哪些文件被添加了

**执行命令**:
```bash
git status
```

**预期输出**:
```
位于分支 main

要提交的变更：
  新文件：   .gitignore
  新文件：   README.md
  新文件：   docs/PRD.md
  新文件：   docs/api-design.md
  ...
```

**说明**: 绿色的 `新文件` 表示已添加到暂存区

---

### Step 12: 提交到本地仓库

**目标**: 将暂存区的文件提交到本地Git仓库

**执行命令**:
```bash
git commit -m "feat: 初始化项目结构，添加开发前文档"
```

**预期输出**:
```
[main xxxxxxx] feat: 初始化项目结构，添加开发前文档
 15 files changed, 500 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 README.md
 ...
```

**说明**: 
- `[main xxxxxxx]` 中的 xxxxxxx 是提交ID
- `15 files changed` 表示15个文件被修改

---

## 第五部分：推送到GitHub

### Step 13: 确保在main分支

**目标**: 确保当前分支是main

**执行命令**:
```bash
git branch -M main
```

**说明**: 这个命令会将当前分支重命名为main

---

### Step 14: 首次推送到GitHub

**目标**: 将本地代码推送到GitHub远程仓库

**执行命令**:
```bash
git push -u origin main
```

**可能出现的情况**:

**情况1**: 直接成功
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
...
To https://github.com/LWT1212/CareerPilot.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

**情况2**: 需要登录
- 浏览器会弹出GitHub登录页面
- 输入用户名和密码
- 或者使用Token认证

**情况3**: 网络错误
```
fatal: RPC failed; curl 22 The requested URL returned error: 408
```
**解决方案**: 稍后重试，或检查网络连接

---

### Step 15: 验证推送成功

**目标**: 确认代码已推送到GitHub

**方法1**: 命令行验证
```bash
git log --oneline
```

**预期输出**:
```
3732b1a docs(journal): 更新开发日志格式，添加详细步骤记录
64ef7b8 docs(journal): 初始化项目开发日志
xxxxxxx feat: 初始化项目结构，添加开发前文档
```

**方法2**: 浏览器验证
1. 打开 https://github.com/LWT1212/CareerPilot
2. 确认文件已上传

---

## 后续Git操作

### 日常提交流程

```bash
# 1. 查看修改了哪些文件
git status

# 2. 添加修改的文件
git add .
# 或者添加特定文件
git add filename.txt

# 3. 提交
git commit -m "feat: 描述你做了什么"

# 4. 推送到GitHub
git push origin main
```

### 拉取最新代码

```bash
git pull origin main
```

### 查看提交历史

```bash
git log --oneline
```

---

## 常见问题

### 问题1: remote origin 已存在

**错误信息**:
```
fatal: remote origin already exists.
```

**解决方案**:
```bash
git remote remove origin
git remote add origin https://github.com/LWT1212/CareerPilot.git
```

---

### 问题2: push 被拒绝

**错误信息**:
```
! [rejected]        main -> main (fetch first)
```

**解决方案**:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

---

### 问题3: 需要输入密码但没弹出

**解决方案**:
```bash
# 使用Token方式推送
git remote set-url origin https://<YOUR_TOKEN>@github.com/LWT1212/CareerPilot.git
git push origin main
```

---

## 命令速查

| 操作 | 命令 |
|------|------|
| 初始化仓库 | `git init` |
| 添加远程仓库 | `git remote add origin URL` |
| 查看远程仓库 | `git remote -v` |
| 添加所有文件 | `git add .` |
| 查看状态 | `git status` |
| 提交 | `git commit -m "message"` |
| 推送 | `git push origin main` |
| 拉取 | `git pull origin main` |
| 查看日志 | `git log --oneline` |
