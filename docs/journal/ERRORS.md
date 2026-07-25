# 常见错误汇总

> 遇到的错误和解决方案，快速查找

---

## Git 相关错误

### ❌ `fatal: remote origin already exists`

**原因**: 远程仓库已存在

**解决**:
```bash
git remote remove origin
git remote add origin https://github.com/用户名/仓库名.git
```

---

### ❌ `fatal: 'origin' does not appear to be a git repository`

**原因**: 远程仓库未添加或添加失败

**解决**:
```bash
git remote add origin https://github.com/用户名/仓库名.git
git remote -v  # 验证
```

---

### ❌ `! [rejected] main -> main (fetch first)`

**原因**: 远程有本地没有的提交

**解决**:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

---

### ❌ `error: failed to push some refs`

**原因**: 分支名不匹配

**解决**:
```bash
git branch -M main
git push -u origin main
```

---

## Docker 相关错误

### ❌ `docker-compose: command not found`

**原因**: 新版Docker使用 `docker compose`（不带横杠）

**解决**:
```bash
docker compose version
```

---

### ❌ `Cannot connect to the Docker daemon`

**原因**: Docker服务未启动

**解决**:
```bash
sudo systemctl start docker
```

---

### ❌ `port is already allocated`

**原因**: 端口被占用

**解决**:
```bash
# 查看占用端口的进程
lsof -i :8000

# 修改docker-compose.yml中的端口映射
ports:
  - "8001:8000"
```

---

## Python 相关错误

### ❌ `ModuleNotFoundError: No module named 'xxx'`

**原因**: 未安装依赖

**解决**:
```bash
pip install xxx
```

---

### ❌ `SyntaxError: invalid syntax`

**原因**: Python语法错误

**解决**: 检查代码缩进、括号、冒号等

---

## Node.js 相关错误

### ❌ `npm ERR! code ENOENT`

**原因**: package.json不存在

**解决**:
```bash
npm init -y
```

---

### ❌ `EACCES permission denied`

**原因**: 权限不足

**解决**:
```bash
sudo npm install -g xxx
# 或者修复npm权限
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
```

---

## 通用错误

### ❌ `Permission denied`

**原因**: 权限不足

**解决**:
```bash
sudo command
# 或者修改文件权限
chmod +x file
```

---

### ❌ `No such file or directory`

**原因**: 文件或目录不存在

**解决**: 检查路径是否正确
```bash
ls -la  # 查看当前目录
pwd     # 查看当前路径
```
