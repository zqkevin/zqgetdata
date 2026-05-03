# 足球数据采集系统 (zqgetdata)

## 项目简介

这是一个完整的足球数据采集、处理和API服务系统，主要功能包括：

- **体彩数据采集**：支持TCZQ（传统足彩）和BJDC（北京单场）数据采集
- **竞彩数据采集**：支持多种玩法的竞彩数据采集
- **数据处理**：球队名称匹配、赔率处理、赛果获取等
- **API服务**：提供RESTful API接口供前端调用

## 项目结构

```
zqgetdata/
├── api/                    # FastAPI后端服务
│   ├── core/              # 核心模块（认证、安全、模型）
│   ├── database/          # 数据库模型
│   ├── routes/            # API路由
│   └── main.py            # API入口
├── get_data/              # 数据采集模块
│   ├── app/
│   │   ├── common/        # 公共工具函数
│   │   ├── crawler/       # 数据采集器
│   │   ├── database/      # 数据库模型
│   │   └── log/           # 日志模块
│   └── main.py            # 采集程序入口
└── temp/                  # 临时文件和测试脚本
```

## 技术栈

- **后端框架**：FastAPI
- **数据库**：MySQL 8.0+
- **数据采集**：Python requests + BeautifulSoup
- **容器化**：Docker & Docker Compose
- **认证**：JWT Token

## 主要功能

### 1. 数据采集
- TCZQ传统足彩数据采集
- BJDC北京单场数据采集
- 自动获取比赛信息、赔率、赛果
- 智能球队名称匹配

### 2. API服务
- 用户认证与授权
- 比赛数据查询
- 赔率数据查询
- 收藏管理

### 3. 数据处理
- 球队名称标准化
- 跨数据源别名匹配
- 赔率变化追踪
- 赛果自动更新

## 快速开始

### 环境要求
- Python 3.9+
- MySQL 8.0+
- Docker (可选)

### 安装依赖
```bash
cd get_data
pip install -r requirements.txt

cd ../api
pip install -r requirements.txt
```

### 配置环境变量
复制 `.env.example` 为 `.env` 并配置数据库连接信息。

### 运行数据采集
```bash
cd get_data
python main.py
```

### 运行API服务
```bash
cd api
python main.py
```

## 分支说明

- `master`: 稳定的生产版本
- `api-development`: API开发分支

## 部署

使用Docker部署（推荐）：
```bash
docker-compose up -d
```

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系项目维护者。
