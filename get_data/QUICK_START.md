# 快速部署指南

## 📦 打包项目（在开发机器上）

### Windows
```powershell
.\package.ps1
```

这会自动：
- ✅ 清理 `__pycache__`、`.pyc` 等临时文件
- ✅ 清理日志文件
- ✅ 清理虚拟环境
- ✅ 生成带时间戳的压缩包：`zqgetdata_20260423_143000.zip`

### 手动打包
```bash
# Linux/Mac
zip -r zqgetdata.zip . -x ".git/*" -x ".venv/*" -x "__pycache__/*" -x "*.log" -x "temp/*"

# 或使用 tar
tar -czf zqgetdata.tar.gz --exclude='.git' --exclude='.venv' --exclude='__pycache__' --exclude='*.log' .
```

## 🚀 部署到服务器

### 1. 上传压缩包
```bash
# 使用 scp
scp zqgetdata_*.zip user@server:/opt/

# 或使用 SFTP/FTP 工具
```

### 2. 解压
```bash
cd /opt
unzip zqgetdata_*.zip
cd zqgetdata
```

### 3. 修改数据库密码
```bash
# 编辑 docker-compose.yml
vim docker-compose.yml

# 修改以下密码（第 81、83、35 行）
MYSQL_ROOT_PASSWORD: your_strong_password
MYSQL_PASSWORD: user_strong_password  
DB_PASSWORD: your_strong_password
```

### 4. 启动服务

#### 方式一：使用启动脚本（推荐）
```bash
chmod +x deploy.sh
./deploy.sh
```

#### 方式二：手动启动
```bash
docker-compose up -d --build
```

### 5. 查看运行状态
```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f zqgetdata

# 查看资源使用
docker stats
```

## 🔧 常用操作

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart zqgetdata
```

### 更新代码
```bash
# 1. 拉取最新代码或上传新版本
git pull

# 2. 重新构建并启动
docker-compose up -d --build
```

### 查看日志
```bash
# 实时日志
docker-compose logs -f zqgetdata

# 最近100行
docker-compose logs --tail=100 zqgetdata
```

### 进入容器
```bash
# 进入采集服务
docker exec -it zqgetdata_collector bash

# 进入 MySQL
docker exec -it zqgetdata_mysql mysql -uroot -p
```

### 备份数据
```bash
# 备份 MySQL 数据
docker exec zqgetdata_mysql mysqldump -uroot -p soccer_data > backup_$(date +%Y%m%d).sql

# 备份日志
tar -czf logs_backup_$(date +%Y%m%d).tar.gz app/log/
```

## ⚙️ 配置说明

### 使用外部 MySQL

如果使用已有的 MySQL 服务器，编辑 `docker-compose.yml`：

1. **删除 mysql 服务**（第 74-130 行）

2. **修改数据库配置**（第 29-35 行）：
```yaml
environment:
  - DB_HOST=192.168.1.100    # 你的 MySQL 地址
  - DB_PORT=3306
  - DB_USER=your_user
  - DB_PASSWORD=your_password
  - DB_NAME=soccer_data
```

3. **删除 depends_on**（第 14-16 行）

4. **启动**：
```bash
docker-compose up -d
```

### 调整资源限制

根据服务器配置调整 `docker-compose.yml`：

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # CPU 上限
      memory: 4G       # 内存上限
    reservations:
      cpus: '1.0'      # CPU 保留
      memory: 1G       # 内存保留
```

### 开启 API 端口

如果需要访问 API 服务，取消注释 `docker-compose.yml` 第 44-45 行：

```yaml
ports:
  - "8000:8000"
```

## 🐛 故障排查

### 容器无法启动
```bash
# 查看详细错误
docker-compose logs zqgetdata

# 检查配置
docker-compose config
```

### 数据库连接失败
```bash
# 检查 MySQL 是否运行
docker-compose ps mysql

# 测试网络连通性
docker exec -it zqgetdata_collector ping mysql

# 查看 MySQL 日志
docker-compose logs mysql
```

### 内存不足
```bash
# 查看内存使用
docker stats

# 调整资源限制后重启
docker-compose up -d
```

### 日志文件过大

Docker 已配置日志轮转：
- 单个文件最大 10MB
- 保留 3 个文件
- 总大小不超过 30MB

如需清理：
```bash
docker-compose down
docker system prune -f
```

## 📊 监控建议

### 1. 容器监控
```bash
# 实时资源监控
docker stats

# 容器状态
docker-compose ps
```

### 2. 应用日志
```bash
# 查看最近的错误
docker-compose logs --tail=50 zqgetdata | grep ERROR

# 查看警告
docker-compose logs --tail=50 zqgetdata | grep WARNING
```

### 3. 数据库监控
```bash
# 连接数
docker exec -it zqgetdata_mysql mysql -uroot -p -e "SHOW STATUS LIKE 'Threads_connected';"

# 慢查询
docker exec -it zqgetdata_mysql mysql -uroot -p -e "SHOW VARIABLES LIKE 'slow_query_log';"
```

## 🔒 安全建议

1. ✅ **修改默认密码**：务必修改所有密码
2. ✅ **不要暴露 MySQL 端口**：除非必要
3. ✅ **使用防火墙**：限制访问 IP
4. ✅ **定期更新**：保持镜像和依赖最新
5. ✅ **备份数据**：定期备份数据库和日志

## 📞 获取帮助

如遇到问题：
1. 查看日志：`docker-compose logs -f`
2. 检查配置：`docker-compose config`
3. 查看文档：`README_DEPLOY.md`
4. 检查 Docker 版本：`docker --version`

---

**祝部署顺利！** 🎉
