# 双数据库架构说明

## 📊 架构概述

本项目采用**双数据库架构**，将体育数据查询和 API 服务管理分离：

```
┌─────────────────────────────────────────────────┐
│           Soccer Data API 服务                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐       ┌──────────────────┐   │
│  │  DataDB      │       │   SelfDB         │   │
│  │ (只读查询)    │       │  (读写操作)       │   │
│  └──────┬───────┘       └────────┬─────────┘   │
│         │                        │              │
│         ▼                        ▼              │
│  ┌──────────────┐       ┌──────────────────┐   │
│  │soccer_data   │       │ soccer_server    │   │
│  │(远程服务器)   │       │  (本地)          │   │
│  └──────────────┘       └──────────────────┘   │
│         │                        │              │
│         ├─ 比赛数据               ├─ 用户表      │
│         ├─ 赔率数据               ├─ 查询日志    │
│         └─ 赛果数据               ├─ Token 管理  │
│                                  └─ 系统配置    │
└─────────────────────────────────────────────────┘
```

## 🗄️ 数据库配置

### 1. soccer_data（体育数据数据库）

**用途**: 存储体育比赛、赔率、赛果等数据（只读查询）

**配置** (`.env`):
```env
DATA_DB_HOST=115.190.125.52
DATA_DB_PORT=3306
DATA_DB_USER=soccer_data
DATA_DB_PASSWORD=pety93033
DATA_DB_NAME=soccer_data
```

**包含的表**:
- `league` - 联赛信息
- `team` - 球队信息
- `team_alias` - 球队别名
- `tczq_match` - 体彩足球比赛
- `tczq_spf_odds` - 胜平负赔率
- `tczq_handicap_spf_odds` - 让球胜平负赔率
- `bjdc_match` - 北京单场比赛
- ... 等其他体育数据表

### 2. soccer_server（API 服务数据库）

**用途**: 存储 API 服务相关的管理数据（读写操作）

**配置** (`.env`):
```env
SERVER_DB_HOST=127.0.0.1
SERVER_DB_PORT=3306
SERVER_DB_USER=soccer_server
SERVER_DB_PASSWORD=pety93033
SERVER_DB_NAME=soccer_server
```

**包含的表**:
- `api_users` - API 用户表
- `query_logs` - 查询日志表
- `api_tokens` - Token 管理表
- `system_config` - 系统配置表

## 💻 代码使用

### 导入数据库类

```python
from database.db_core import DataDB, SelfDB
```

### 使用 DataDB（查询体育数据）

```python
from database.db_core import DataDB
from database.tczq_models import TczqMatch

# 创建实例
db = DataDB()

try:
    # 查询比赛列表
    matches = db.query(TczqMatch).filter(
        TczqMatch.status == 0
    ).limit(10).all()
    
    for match in matches:
        print(f"{match.match_num_str}: {match.match_time}")
finally:
    db.close()
```

### 使用 SelfDB（操作用户/日志）

```python
from database.db_core import SelfDB
from database.server_models import User, QueryLog

# 创建实例
db = SelfDB()

try:
    # 查询用户
    user = db.query(User).filter(
        User.username == "admin"
    ).first()
    
    if user:
        print(f"用户: {user.username}, 管理员: {user.is_admin}")
    
    # 记录查询日志
    log = QueryLog(
        username="admin",
        endpoint="/api/tczq/matches",
        method="GET",
        response_status=200,
        response_time=0.15
    )
    db.add(log)
    
finally:
    db.close()
```

## 🔄 初始化数据库

### 创建 soccer_server 数据库表

```bash
cd api
python init_server_db.py
```

这会创建以下表：
- ✅ `api_users` - 用户表
- ✅ `query_logs` - 查询日志表
- ✅ `api_tokens` - Token 表
- ✅ `system_config` - 系统配置表

### 自动创建默认管理员

启动 API 服务时，会自动检查并创建默认管理员账户：
- 用户名: `admin`
- 密码: `admin123`

## 📝 数据模型

### User（用户表）

```python
class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)  # 用户名
    hashed_password = Column(String(255))  # 加密密码
    email = Column(String(100))  # 邮箱
    is_active = Column(Boolean, default=True)  # 是否激活
    is_admin = Column(Boolean, default=False)  # 是否管理员
    remark = Column(Text)  # 备注
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### QueryLog（查询日志表）

```python
class QueryLog(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)  # 用户ID
    username = Column(String(50), index=True)  # 用户名
    endpoint = Column(String(200))  # API端点
    method = Column(String(10))  # HTTP方法
    params = Column(Text)  # 请求参数
    ip_address = Column(String(50))  # IP地址
    response_status = Column(Integer)  # 响应状态码
    response_time = Column(Float)  # 响应时间(秒)
    error_message = Column(Text)  # 错误信息
    created_at = Column(DateTime, index=True)
```

## 🔧 配置修改

如需修改数据库连接信息，编辑 `.env` 文件：

```env
# 体育数据数据库
DATA_DB_HOST=your_host
DATA_DB_PORT=3306
DATA_DB_USER=your_user
DATA_DB_PASSWORD=your_password
DATA_DB_NAME=soccer_data

# API服务数据库
SERVER_DB_HOST=127.0.0.1
SERVER_DB_PORT=3306
SERVER_DB_USER=soccer_server
SERVER_DB_PASSWORD=your_password
SERVER_DB_NAME=soccer_server
```

修改后重启服务即可生效。

## 🎯 最佳实践

### 1. 选择合适的数据库类

- **查询比赛、赔率、赛果** → 使用 `DataDB()`
- **操作用户、日志、配置** → 使用 `SelfDB()`

### 2. 始终关闭数据库连接

```python
db = DataDB()  # 或 SelfDB()
try:
    # 执行数据库操作
    result = db.query(...).all()
finally:
    db.close()  # 确保连接被关闭
```

### 3. 使用事务

```python
db = SelfDB()
try:
    # 多个操作
    db.add(user)
    db.add(log)
    db.commit()  # 提交事务
except Exception as e:
    db.rollback()  # 出错时回滚
    raise e
finally:
    db.close()
```

### 4. 记录查询日志

在重要的查询接口中添加日志记录：

```python
from database.server_models import QueryLog
import time

start_time = time.time()
try:
    # 执行查询
    matches = db.query(TczqMatch).all()
    response_time = time.time() - start_time
    
    # 记录成功日志
    log = QueryLog(
        username=current_user.get("username"),
        endpoint="/api/tczq/matches",
        method="GET",
        response_status=200,
        response_time=response_time
    )
    selfdb.add(log)
    
except Exception as e:
    response_time = time.time() - start_time
    
    # 记录错误日志
    log = QueryLog(
        username=current_user.get("username"),
        endpoint="/api/tczq/matches",
        method="GET",
        response_status=500,
        response_time=response_time,
        error_message=str(e)
    )
    selfdb.add(log)
```

## 🔍 故障排查

### 问题1: 连接失败

**错误**: `Can't connect to MySQL server`

**解决**:
1. 检查 `.env` 中的数据库配置是否正确
2. 确认数据库服务正在运行
3. 检查网络连接（特别是远程数据库）
4. 验证用户名和密码

### 问题2: 表不存在

**错误**: `Table 'xxx' doesn't exist`

**解决**:
```bash
# 运行初始化脚本
python init_server_db.py
```

### 问题3: 索引太长

**错误**: `Specified key was too long; max key length is 1000 bytes`

**解决**: 
- 避免对超过 255 字符的字段创建索引
- 使用 `String(191)` 代替 `String(255)`（对于 utf8mb4）
- 或者移除不必要的索引

## 📊 性能优化建议

1. **连接池配置**
   - DataDB: pool_size=15, max_overflow=30（高并发查询）
   - SelfDB: pool_size=5, max_overflow=10（低频次操作）

2. **查询优化**
   - 使用分页限制返回数量
   - 添加适当的数据库索引
   - 避免 N+1 查询问题

3. **日志策略**
   - 定期清理旧的查询日志
   - 异步记录日志（可选）
   - 重要操作才记录日志

---

**更新日期**: 2026-04-27  
**版本**: 1.0.0
