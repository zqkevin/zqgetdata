# 使用官方Python镜像作为基础
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制宿主机挂载的requirements.txt并安装依赖
COPY requirements.txt .
# 注意：这里会使用挂载到/app目录下的requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 设置容器启动时执行的命令
CMD ["python", "get_zq_data.py"]