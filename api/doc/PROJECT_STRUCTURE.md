# API 项目目录结构说明

## 📁 完整目录树

```
api/
├── core/                    # 核心模块
│   ├── __init__.py
│   ├── security.py         # JWT 认证、密码加密
│   ├── deps.py             # FastAPI 依赖注入（认证）
│   └── models.py           # Pydantic 数据模型
│
├── database/               # 数据库模块
│   ├── __init__.py         # 导出数据库类和实例
│   ├── db_core.py          # 数据库核心操作类 (DataDB, SelfDB)
│   ├── base_models.py      # 基础模型（联赛、球队等）
│   ├── tczq_models.py      # 体彩足球模型
│   ├── bjdc_models.py      # 北京单场模型
│   ├── tcbk_models.py      # 体彩篮球模型
│   ├── digital_lottery_models.py  # 数字彩票模型
│   └── server_models.py    # API 服务模型（用户、日志等）⭐ 新增
│
├── routes/                 # API 路由
│   ├── __init__.py
│   ├── auth.py             # 认证路由（登录、注册）
│   ├── tczq.py             # 体彩足球接口
│   ├── bjdc.py             # 北京单场接口
│   └── base.py             # 基础数据接口
│
├── test/                   # 测试脚本 ⭐ 新增
│   ├── __init__.py
│   └── test_api.py         # API 功能测试脚本
│
├── doc/                    # 文档目录 ⭐ 新增
│   ├── __init__.py
│   ├── API_DOCUMENTATION.md        # API 接口文档
│   ├── TEST_REPORT.md              # 测试报告
│   ├── DUAL_DATABASE_ARCHITECTURE.md  # 双数据库架构说明
│   └── PROJECT_STRUCTURE.md        # 本文档
│
├── config.py               # 应用配置（环境变量）
├── main.py                 # FastAPI 应用入口
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置
├── .env.example            # 环境变量示例
├── start.bat               # Windows 启动脚本
├── init_server_db.py       # 数据库初始化脚本
├── README.md               # 项目说明
├── SECURITY_UPDATES.md     # 安全更新日志
└── DUAL_DATABASE_ARCHITECTURE.md  # 双数据库架构说明
```

---

## 📂 目录详细说明

### core/ - 核心模块

存放项目的核心功能代码，不依赖于具体业务。

#### `security.py`
- **功能**: JWT Token 生成和验证、密码加密
- **主要函数**:
  - `create_access_token()` - 创建 JWT Token
  - `decode_access_token()` - 解码 JWT Token
  - `verify_password()` - 验证密码
  - `get_password_hash()` - 密码哈希

#### `deps.py`
- **功能**: FastAPI 依赖注入
- **主要依赖**:
  - `get_current_user` - 获取当前登录用户（用于路由保护）

#### `models.py`
- **功能**: Pydantic 数据模型定义
- **包含模型**:
  - `Token` - Token 响应模型
  - `UserLogin` - 登录请求模型
  - `UserCreate` - 注册请求模型
  - `ResponseModel` - 统一响应模型
  - 各业务接口的响应模型

---

### database/ - 数据库模块

封装所有数据库操作，实现双数据库架构。

#### `db_core.py` ⭐ 核心文件
- **功能**: 数据库连接和操作封装
- **主要类**:
  - `QueryWrapper` - 查询包装器（自动重试、连接保活）
  - `DataDB` - 体育数据数据库操作类（soccer_data）
  - `SelfDB` - API 服务数据库操作类（soccer_server）
  - `mydb` - DataDB 的别名（向后兼容）

**特性**:
- ✅ 连接池管理
- ✅ 自动重连机制
- ✅ 指数退避重试
- ✅ 事务支持

#### `server_models.py` ⭐ 新增
- **功能**: API 服务专用数据模型
- **包含表**:
  - `User` - 用户表
  - `QueryLog` - 查询日志表
  - `ApiToken` - Token 管理表
  - `SystemConfig` - 系统配置表

#### 其他模型文件
从 `app/database` 复制而来，保持与原项目一致：
- `base_models.py` - 联赛、球队等基础表
- `tczq_models.py` - 体彩足球相关表
- `bjdc_models.py` - 北京单场相关表
- `tcbk_models.py` - 体彩篮球相关表
- `digital_lottery_models.py` - 数字彩票相关表

#### `__init__.py`
- **功能**: 导出所有数据库类和实例
- **导出的实例**:
  - `datadb` - DataDB 实例
  - `selfdb` - SelfDB 实例
  - `localdb` - datadb 的别名（向后兼容）

---

### routes/ - API 路由

定义所有 RESTful API 端点。

#### `auth.py`
- **路径前缀**: `/api/auth`
- **接口**:
  - `POST /login` - 用户登录
  - `POST /register` - 用户注册
- **特性**: 
  - 启动时自动创建默认管理员
  - 使用 SelfDB 操作用户数据

#### `tczq.py`
- **路径前缀**: `/api/tczq`
- **接口**:
  - `GET /matches` - 比赛列表
  - `GET /match/{match_id}` - 比赛详情
  - `GET /odds/spf` - 胜平负赔率
  - `GET /results` - 比赛结果
- **数据库**: 使用 DataDB 查询

#### `bjdc.py`
- **路径前缀**: `/api/bjdc`
- **接口**:
  - `GET /matches` - 比赛列表
  - `GET /match/{match_id}` - 比赛详情
  - `GET /results` - 比赛结果
- **数据库**: 使用 DataDB 查询

#### `base.py`
- **路径前缀**: `/api/base`
- **接口**:
  - `GET /leagues` - 联赛列表
  - `GET /teams` - 球队列表
  - `GET /team/{team_id}/aliases` - 球队别名
- **数据库**: 使用 DataDB 查询

---

### test/ - 测试脚本 ⭐ 新增

存放自动化测试脚本。

#### `test_api.py`
- **功能**: 完整的 API 功能测试
- **测试覆盖**:
  1. 健康检查
  2. 用户登录
  3. 用户注册
  4. 体彩足球比赛列表
  5. 体彩足球比赛详情
  6. 北京单场比赛列表
  7. 联赛列表
  8. 球队列表
  9. 未授权访问拦截
  10. 无效 Token 拦截

**运行方式**:
```bash
python test/test_api.py
```

---

### doc/ - 文档目录 ⭐ 新增

存放所有项目文档。

#### `API_DOCUMENTATION.md`
- **内容**: 完整的 API 接口文档
- **包含**:
  - 认证机制说明
  - 所有接口详细说明
  - 请求/响应示例
  - 错误码说明
  - 常见问题

#### `TEST_REPORT.md`
- **内容**: 自动化测试报告
- **包含**:
  - 测试结果统计
  - 每个测试的详细信息
  - 性能指标
  - 安全性评估
  - 改进建议

#### `DUAL_DATABASE_ARCHITECTURE.md`
- **内容**: 双数据库架构详细说明
- **包含**:
  - 架构图
  - 配置说明
  - 使用示例
  - 最佳实践
  - 故障排查

#### `PROJECT_STRUCTURE.md`
- **内容**: 本文档，项目结构说明

---

## 🔧 配置文件

### `config.py`
- **功能**: 应用配置管理
- **使用**: Pydantic Settings
- **配置项**:
  - 应用信息（名称、版本）
  - 服务器配置（Host、Port）
  - 双数据库配置（DATA_DB_*, SERVER_DB_*）
  - JWT 配置（SECRET_KEY、过期时间）
  - CORS 配置

### `.env`
- **功能**: 环境变量配置（不应提交到 Git）
- **示例**:
  ```env
  DATA_DB_HOST=115.190.125.52
  DATA_DB_USER=soccer_data
  DATA_DB_PASSWORD=pety93033
  
  SERVER_DB_HOST=127.0.0.1
  SERVER_DB_USER=soccer_server
  SERVER_DB_PASSWORD=pety93033
  
  SECRET_KEY=your-secret-key
  ```

### `.env.example`
- **功能**: 环境变量示例模板
- **用途**: 提供给开发者参考

### `requirements.txt`
- **功能**: Python 依赖清单
- **关键依赖**:
  - fastapi==0.109.0
  - uvicorn==0.27.0
  - sqlalchemy==2.0.45
  - pymysql==1.1.1
  - python-jose[cryptography]==3.3.0
  - cryptography>=46.0.5
  - passlib==1.7.4
  - bcrypt==4.0.1

---

## 🚀 启动文件

### `main.py`
- **功能**: FastAPI 应用入口
- **职责**:
  - 创建 FastAPI 应用实例
  - 注册中间件（CORS）
  - 注册路由
  - 启动 Uvicorn 服务器

**运行方式**:
```bash
python main.py
```

### `start.bat`
- **功能**: Windows 一键启动脚本
- **内容**:
  ```batch
  @echo off
  cd /d %~dp0
  python main.py
  pause
  ```

### `init_server_db.py`
- **功能**: 初始化 soccer_server 数据库
- **执行内容**:
  - 创建 api_users 表
  - 创建 query_logs 表
  - 创建 api_tokens 表
  - 创建 system_config 表

**运行方式**:
```bash
python init_server_db.py
```

---

## 📊 数据流向

```
客户端请求
    ↓
FastAPI (main.py)
    ↓
路由层 (routes/)
    ↓
    ├─→ 认证检查 (core/deps.py)
    │       ↓
    │   JWT 验证 (core/security.py)
    │       ↓
    │   用户数据 (SelfDB → soccer_server)
    │
    ├─→ 业务逻辑
    │       ↓
    │   数据查询 (DataDB → soccer_data)
    │       ↓
    │   返回结果
    │
    └─→ 响应格式化 (core/models.py)
            ↓
        客户端接收
```

---

## 🎯 关键设计原则

### 1. 职责分离
- **core/**: 通用功能，不依赖业务
- **database/**: 数据访问层
- **routes/**: API 接口层
- **test/**: 测试代码
- **doc/**: 文档

### 2. 双数据库隔离
- **DataDB**: 只读查询体育数据
- **SelfDB**: 读写 API 服务数据
- 互不干扰，独立优化

### 3. 统一响应格式
所有接口返回统一的 `ResponseModel`:
```json
{
  "code": 200,
  "message": "success",
  "data": {...},
  "total": 10
}
```

### 4. 认证保护
- 所有业务接口需要 JWT Token
- 使用 FastAPI Depends 机制
- 未授权自动返回 401

### 5. 向后兼容
- 保留 `mydb` 作为 `DataDB` 别名
- 保留 `localdb` 作为 `datadb` 别名
- 旧代码无需修改即可运行

---

## 📝 开发规范

### 添加新接口

1. **在 routes/ 中创建或修改路由文件**
   ```python
   from fastapi import APIRouter, Depends
   from database.db_core import DataDB
   from core.deps import get_current_user
   
   router = APIRouter(prefix="/new_module", tags=["新模块"])
   
   @router.get("/items")
   async def get_items(current_user: dict = Depends(get_current_user)):
       db = DataDB()
       try:
           items = db.query(...).all()
           return {"code": 200, "data": items}
       finally:
           db.close()
   ```

2. **在 main.py 中注册路由**
   ```python
   from routes.new_module import router as new_router
   app.include_router(new_router, prefix="/api")
   ```

3. **在 test/test_api.py 中添加测试**
   ```python
   def test_new_module(token):
       headers = {"Authorization": f"Bearer {token}"}
       response = requests.get(f"{BASE_URL}/api/new_module/items", headers=headers)
       assert response.status_code == 200
   ```

4. **在 doc/API_DOCUMENTATION.md 中添加文档**

### 添加新数据表

1. **在 database/ 中创建模型文件**
   ```python
   from sqlalchemy import Column, Integer, String
   from .base_models import Base
   
   class NewTable(Base):
       __tablename__ = 'new_table'
       id = Column(Integer, primary_key=True)
       name = Column(String(100))
   ```

2. **在 database/__init__.py 中导出**
   ```python
   from .new_models import NewTable
   __all__ = [..., 'NewTable']
   ```

3. **如需在 soccer_server 中使用，添加到 server_models.py**

---

## 🔍 调试技巧

### 查看日志
Uvicorn 会自动输出请求日志：
```
INFO:     127.0.0.1:12345 - "GET /api/tczq/matches HTTP/1.1" 200 OK
```

### 交互式文档
访问 Swagger UI:
```
http://localhost:8000/docs
```

可以直接在浏览器中测试所有接口。

### 数据库调试
```python
from database.db_core import DataDB, SelfDB

# 测试 DataDB
db = DataDB()
print(db.query(...).first())
db.close()

# 测试 SelfDB
db = SelfDB()
print(db.query(...).first())
db.close()
```

---

## 📦 部署注意事项

### 生产环境配置

1. **修改 .env**
   ```env
   DEBUG=False
   SECRET_KEY=<强随机密钥>
   ALLOWED_ORIGINS=["https://yourdomain.com"]
   ```

2. **修改默认密码**
   - 登录后立即修改 admin 密码
   - 或删除默认账户

3. **启用 HTTPS**
   - 使用 Nginx 反向代理
   - 或使用 Let's Encrypt

4. **配置进程管理器**
   - 使用 Supervisor 或 systemd
   - 或使用 Docker

5. **监控和日志**
   - 配置日志轮转
   - 添加性能监控
   - 设置告警机制

---

**文档版本**: 1.0.0  
**最后更新**: 2026-04-27  
**维护者**: Soccer Data API Team
