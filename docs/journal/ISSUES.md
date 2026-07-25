# 问题记录

---

## Issue #1: docker-compose 命令不存在

**日期**: 2024-01-25
**阶段**: Phase 0 - 环境准备
**状态**: 🟢 已解决
**优先级**: P1

### 问题描述
运行 `docker-compose --version` 提示命令不存在

### 原因分析
Docker 29.x 版本已经将 docker-compose 作为内置子命令，不再需要单独安装

### 解决方案
使用 `docker compose`（不带横杠）替代 `docker-compose`

### 经验教训
新版本软件可能会改变命令行接口，遇到问题先检查版本和文档

---

## Issue #2: ChatGPT共享链接无法访问

**日期**: 2024-01-25
**阶段**: Phase 0 - PRD获取
**状态**: 🟢 已解决
**优先级**: P2

### 问题描述
访问 https://chatgpt.com/share/... 链接超时

### 原因分析
ChatGPT共享链接可能需要登录或网络问题

### 解决方案
让用户直接上传PRD文件（.odt格式），使用命令提取文本内容

### 经验教训
外部链接可能不稳定，重要文档应该有本地备份

---

## Issue #3: ODT文件无法直接读取

**日期**: 2024-01-25
**阶段**: Phase 0 - PRD获取
**状态**: 🟢 已解决
**优先级**: P2

### 问题描述
`.odt` 文件是二进制格式，无法直接读取

### 解决方案
使用 `unzip -p` 命令提取 content.xml，再用 sed 去除XML标签

```bash
unzip -p file.odt content.xml | sed -e 's/<[^>]*>//g'
```

### 经验教训
ODT本质是ZIP压缩包，包含XML文件，可以这样提取内容

---

## Issue #4: Git remote 添加失败

**日期**: 2024-01-25
**阶段**: Phase 0 - Git初始化
**状态**: 🟢 已解决
**优先级**: P1

### 问题描述
执行 `git push` 报错 `fatal: 'origin' does not appear to be a git repository`

### 原因分析
远程仓库地址添加失败或未添加

### 解决方案
重新添加远程仓库：
```bash
git remote remove origin 2>/dev/null
git remote add origin https://github.com/LWT1212/CareerPilot.git
git remote -v  # 验证
```

### 经验教训
添加远程仓库后，用 `git remote -v` 验证是否成功
