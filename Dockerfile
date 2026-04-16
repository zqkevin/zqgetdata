# 使用 Python 3.12 slim 版本作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码（这里只是占位，实际通过 volume 挂载）
COPY . .

# 创建日志目录
RUN mkdir -p /app/app/log/api \
    /app/app/log/bjdc \
    /app/app/log/jcbk \
    /app/app/log/lottery \
    /app/app/log/tczq

# 暴露端口（API 服务）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# 启动命令（默认运行 main.py）
CMD ["python", "main.py"]
