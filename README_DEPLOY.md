# Docker 部署指南

## 📦 项目结构

```
zqgetdata/
├── app/                    # 应用代码
│   ├── api/               # API 接口
│   ├── common/            # 公共模块
│   ├── crawler/           # 爬虫模块
│   ├── database/          # 数据库模型
│   └── log/               # 日志目录（挂载到宿主机）
├── temp/                  # 临时文件（不打包到镜像）
├── tests/                 # 测试文件（不打包到镜像）
├── doc/                   # 文档（不打包到镜像）
├── main.py                # 主程序入口
├── config.py              # 配置文件
├── requirements.txt       # Python 依赖
├── Dockerfile             # Docker 镜像构建文件
└── docker-compose.yml     # Docker Compose 配置
```

## 🚀 快速开始

### 方式一：使用内置 MySQL（推荐新手）

1. **修改数据库密码**
   ```bash
   # 编辑 docker-compose.yml，修改以下密码
   MYSQL_ROOT_PASSWORD: your_password      # 改为强密码
   MYSQL_PASSWORD: user_password           # 改为强密码
   DB_PASSWORD: your_password              # 与 MYSQL_ROOT_PASSWORD 保持一致
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **查看日志**
   ```bash
   docker-compose logs -f zqgetdata
   ```

### 方式二：使用外部 MySQL

1. **删除 docker-compose.yml 中的 mysql 服务部分**（第 74-130 行）

2. **修改数据库配置**
   ```yaml
   environment:
     - DB_HOST=your_mysql_host    # 外部 MySQL 地址
     - DB_PORT=3306
     - DB_USER=your_username
     - DB_PASSWORD=your_password
     - DB_NAME=soccer_data
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TZ` | 时区 | `Asia/Shanghai` |
| `DB_HOST` | MySQL 主机地址 | `mysql` |
| `DB_PORT` | MySQL 端口 | `3306` |
| `DB_USER` | 数据库用户名 | `root` |
| `DB_PASSWORD` | 数据库密码 | `your_password` |
| `DB_NAME` | 数据库名称 | `soccer_data` |

### 数据持久化

#### 日志持久化
```yaml
volumes:
  - ./app/log:/app/app/log  # 日志挂载到当前目录
```

#### MySQL 数据持久化（使用内置 MySQL 时）
```yaml
volumes:
  mysql-data:/var/lib/mysql  # Docker 管理的命名卷
```

### 资源限制

可根据服务器配置调整：
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # CPU 上限
      memory: 2G       # 内存上限
    reservations:
      cpus: '0.5'      # CPU 保留
      memory: 512M     # 内存保留
```

## 🔧 常用命令

### 启动服务
```bash
docker-compose up -d
```

### 停止服务
```bash
docker-compose down
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f zqgetdata
docker-compose logs -f mysql
```

### 重启服务
```bash
docker-compose restart zqgetdata
```

### 进入容器
```bash
# 进入采集服务容器
docker exec -it zqgetdata_collector bash

# 进入 MySQL 容器
docker exec -it zqgetdata_mysql bash
```

### 更新代码
```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并启动
docker-compose up -d --build
```

### 查看容器状态
```bash
docker-compose ps
```

## 📊 数据库初始化

首次启动时，程序会自动创建所需的表结构。如果需要手动初始化：

```bash
# 进入容器
docker exec -it zqgetdata_collector bash

# 运行初始化脚本
python -c "from app.common.init_db import init_database; init_database()"
```

## 🔍 故障排查

### 1. 容器无法启动
```bash
# 查看详细日志
docker-compose logs zqgetdata

# 检查配置文件
docker-compose config
```

### 2. 数据库连接失败
```bash
# 检查 MySQL 是否正常运行
docker-compose ps mysql

# 查看 MySQL 日志
docker-compose logs mysql

# 测试网络连接
docker exec -it zqgetdata_collector ping mysql
```

### 3. 日志文件过大
日志已通过 Docker 的 logging 配置自动轮转：
- 单个文件最大 10MB
- 保留 3 个文件
- 总大小不超过 30MB

如需调整，修改 `docker-compose.yml` 中的 `logging` 配置。

### 4. 内存不足
调整 `docker-compose.yml` 中的资源限制：
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # 增加内存限制
```

## 🛡️ 安全建议

1. **修改默认密码**：务必修改 `docker-compose.yml` 中的所有密码
2. **不要暴露 MySQL 端口**：除非必要，注释掉 `ports: - "3306:3306"`
3. **使用 .env 文件**：敏感信息建议放在 `.env` 文件中
4. **定期更新镜像**：`docker-compose pull && docker-compose up -d`

## 📝 使用 .env 文件（可选）

创建 `.env` 文件：
```env
# 数据库配置
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=soccer_data

# MySQL Root 密码
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_PASSWORD=user_secure_password
```

修改 `docker-compose.yml` 引用变量：
```yaml
environment:
  - DB_HOST=${DB_HOST}
  - DB_PASSWORD=${DB_PASSWORD}
```

## 🎯 生产环境建议

1. **使用外部 MySQL**：更稳定，便于备份和管理
2. **配置监控**：使用 Prometheus + Grafana 监控容器状态
3. **定期备份**：备份 MySQL 数据和日志文件
4. **日志聚合**：使用 ELK 或类似方案集中管理日志
5. **网络隔离**：使用独立的 Docker 网络，限制访问权限

## 📞 技术支持

如有问题，请检查：
1. Docker 版本 >= 20.10
2. Docker Compose 版本 >= 1.29
3. 服务器至少有 2GB 可用内存
4. 防火墙允许必要的端口通信
