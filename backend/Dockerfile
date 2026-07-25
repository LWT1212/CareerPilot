# 使用Python 3.11精简版作为基础镜像
FROM python:3.11-slim

# 设置工作目录（容器内的目录）
WORKDIR /app

# 安装系统依赖（编译C扩展需要）
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件（利用Docker缓存，加快构建）
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
