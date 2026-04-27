# Soccer Data API

基于 FastAPI 的体育数据查询 API 服务，提供体彩足球、北京单场等数据的查询接口。

## 项目结构

```
api/
├── core/               # 核心模块
│   ├── security.py    # JWT 认证
│   ├── deps.py        # 依赖注入
│   └── models.py      # Pydantic 模型
├── database/          # 数据库模块（从 app/database 复制）
│   ├── db_core.py     # 数据库操作封装
│   ├── base_models.py # 基础模型
│   ├── tczq_models.py # 体彩足球模型
│   └── bjdc_models.py # 北京单场模型
├── routes/            # API 路由
│   ├── auth.py        # 认证路由
│   ├── tczq.py        # 体彩足球路由
│   ├── bjdc.py        # 北京单场路由
│   └── base.py        # 基础数据路由
├── config.py          # 配置文件
├── main.py            # 应用入口
└── requirements.txt   # 依赖包
```

## 快速开始

### 1. 安装依赖

```bash
cd api
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=soccer
DB_PASSWORD=123456
DB_NAME=soccer_data

SECRET_KEY=your-secret-key-change-in-production
```

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 认证接口

- `POST /api/auth/login` - 用户登录获取令牌
- `POST /api/auth/register` - 用户注册

默认管理员账号：
- 用户名：admin
- 密码：admin123

### 体彩足球接口

- `GET /api/tczq/matches` - 查询比赛列表
- `GET /api/tczq/match/{match_id}` - 查询比赛详情
- `GET /api/tczq/odds/spf` - 查询胜平负赔率
- `GET /api/tczq/results` - 查询比赛结果

### 北京单场接口

- `GET /api/bjdc/matches` - 查询比赛列表
- `GET /api/bjdc/match/{match_id}` - 查询比赛详情
- `GET /api/bjdc/results` - 查询比赛结果

### 基础数据接口

- `GET /api/base/leagues` - 查询联赛列表
- `GET /api/base/teams` - 查询球队列表
- `GET /api/base/team/{team_id}/aliases` - 查询球队别名

## 使用示例

### 1. 登录获取 Token

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. 查询比赛列表

```bash
curl -X GET "http://localhost:8000/api/tczq/matches?issue=20260427&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 查询比赛详情

```bash
curl -X GET "http://localhost:8000/api/tczq/match/1234567" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 特性

- ✅ JWT 认证机制
- ✅ 完整的 API 文档（Swagger UI）
- ✅ CORS 支持
- ✅ 复用现有数据库模型和操作封装
- ✅ 分页和过滤查询
- ✅ 统一的响应格式

## 注意事项

1. **生产环境**请务必修改 `SECRET_KEY` 为强密钥
2. 建议在生产环境中使用 HTTPS
3. 可以根据需要扩展更多查询接口
4. 默认用户数据存储在内存中，生产环境建议使用数据库存储

## 开发

添加新接口的步骤：

1. 在 `routes/` 目录下创建新的路由文件
2. 定义 Pydantic 模型（如需要）在 `core/models.py`
3. 在 `main.py` 中注册路由
4. 更新本文档

## 许可证

MIT

## 🔒 安全说明

本项目重视安全性，定期更新依赖包以修复已知漏洞。

### 最新安全更新

- **2026-04-27**: 修复 CVE-2026-26007 (cryptography < 46.0.5)
  - 已将 cryptography 升级到 47.0.0
  - 详见 [SECURITY_UPDATES.md](SECURITY_UPDATES.md)

### 安全最佳实践

1. **生产环境配置**
   - 修改 `.env` 中的 `SECRET_KEY` 为强密钥
   - 使用 HTTPS 部署
   - 启用 CORS 白名单而非 `*`

2. **依赖管理**
   - 定期运行 `pip audit` 检查漏洞
   - 及时更新 requirements.txt 中的包版本
   - 查看 SECURITY_UPDATES.md 了解历史更新

3. **认证安全**
   - JWT Token 有效期设置为 30 分钟（可调整）
   - 密码使用 bcrypt 加密存储
   - 建议实现刷新令牌机制
