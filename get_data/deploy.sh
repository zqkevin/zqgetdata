#!/bin/bash
# ============================================
# Docker 部署启动脚本
# ============================================

set -e

echo "=========================================="
echo "  体育彩票数据采集系统 - Docker 部署"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 确定使用的 docker-compose 命令
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "✅ Docker 版本: $(docker --version)"
echo "✅ Docker Compose 版本: $($DOCKER_COMPOSE version --short)"
echo ""

# 检查配置文件
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: docker-compose.yml 文件不存在"
    exit 1
fi

# 提示用户修改密码
echo "⚠️  重要提示："
echo "   在首次启动前，请确保已修改 docker-compose.yml 中的数据库密码！"
echo "   - MYSQL_ROOT_PASSWORD"
echo "   - MYSQL_PASSWORD"
echo "   - DB_PASSWORD"
echo ""

read -p "是否已修改密码？(y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 请先修改密码后再启动"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p app/log/api
mkdir -p app/log/bjdc
mkdir -p app/log/jcbk
mkdir -p app/log/lottery
mkdir -p app/log/tczq
echo "✅ 目录创建完成"
echo ""

# 构建并启动服务
echo "🚀 正在构建和启动服务..."
$DOCKER_COMPOSE up -d --build

echo ""
echo "=========================================="
echo "  ✅ 服务启动成功！"
echo "=========================================="
echo ""
echo "📊 查看服务状态:"
echo "   $DOCKER_COMPOSE ps"
echo ""
echo "📝 查看日志:"
echo "   $DOCKER_COMPOSE logs -f zqgetdata"
echo ""
echo "🛑 停止服务:"
echo "   $DOCKER_COMPOSE down"
echo ""
echo "🔧 进入容器:"
echo "   docker exec -it zqgetdata_collector bash"
echo ""
