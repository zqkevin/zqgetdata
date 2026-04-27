# 数据库目录结构说明

## 📁 目录组织

为了便于管理和维护，database 目录按**数据库类型**和**功能模块**进行分层组织：

```
database/
├── __init__.py                  # 统一导出所有模型和数据库实例
├── db_core.py                   # 数据库核心操作类 (DataDB, SelfDB)
│
├── data_models/                 # 体育数据模型（soccer_data 数据库）⭐
│   ├── __init__.py              # 导出所有体育数据模型
│   ├── base_models.py           # 基础模型（联赛、球队等）
│   ├── tczq_models.py           # 体彩足球模型
│   ├── bjdc_models.py           # 北京单场模型
│   ├── tcbk_models.py           # 体彩篮球模型
│   └── digital_lottery_models.py # 数字彩票模型
│
└── server_models/               # API 服务模型（soccer_server 数据库）⭐
    ├── __init__.py              # 导出所有服务模型
    ├── user_models.py           # 用户相关（用户信息、等级、余额）
    ├── bet_models.py            # 投注相关（投注记录、订单）
    ├── favorite_models.py       # 收藏/关注相关
    └── system_models.py         # 系统相关（日志、配置、Token）
```

---

## 🗄️ 数据库分类

### 1. data_models/ - 体育数据模型

**数据库**: `soccer_data`（远程服务器）  
**用途**: 存储体育比赛、赔率、赛果等数据  
**权限**: 只读查询  
**操作类**: `DataDB()`

#### 包含的模块

| 文件 | 说明 | 主要表 |
|------|------|--------|
| `base_models.py` | 基础数据 | league, team, team_alias |
| `tczq_models.py` | 体彩足球 | tczq_match, tczq_spf_odds, tczq_result 等 |
| `bjdc_models.py` | 北京单场 | bjdc_match, bjdc_spf_odds, bjdc_result 等 |
| `tcbk_models.py` | 体彩篮球 | tcbk_match, tcbk_spf, tcbk_result 等 |
| `digital_lottery_models.py` | 数字彩票 | digital_lottery_draw, prize 等 |

#### 使用示例

```python
from database.data_models import TczqMatch, League
from database.db_core import DataDB

db = DataDB()
try:
    matches = db.query(TczqMatch).limit(10).all()
finally:
    db.close()
```

---

### 2. server_models/ - API 服务模型

**数据库**: `soccer_server`（本地）  
**用途**: 用户管理、投注记录、系统配置等  
**权限**: 读写操作  
**操作类**: `SelfDB()`

#### 包含的模块

##### user_models.py - 用户相关 ⭐

类似 okooo.com 的完整用户系统：

| 模型 | 表名 | 说明 |
|------|------|------|
| `User` | api_users | 用户基本信息、等级、余额、积分等 |
| `UserLevelConfig` | user_level_config | 等级配置（青铜、白银、黄金等） |
| `UserBalanceLog` | user_balance_logs | 余额变动日志 |

**User 表字段**:
- **基本信息**: username, email, phone, nickname, avatar_url
- **等级系统**: level, experience, vip_level
- **财务信息**: balance, frozen_balance, total_recharge, total_bet, total_win
- **积分系统**: points
- **状态**: is_active, is_admin, is_vip, last_login_at
- **其他**: external_link（个人主页外链）

##### bet_models.py - 投注相关 ⭐

| 模型 | 表名 | 说明 |
|------|------|------|
| `BetRecord` | bet_records | 单注投注记录 |
| `BetOrder` | bet_orders | 串关订单 |

**BetRecord 表字段**:
- match_id, league_name, home_team, away_team
- bet_type (spf/handicap/total_goal/score)
- bet_option, odds, handicap
- bet_amount, potential_win, actual_win
- status (pending/won/lost/refunded)

##### favorite_models.py - 收藏/关注 ⭐

| 模型 | 表名 | 说明 |
|------|------|------|
| `UserFavorite` | user_favorites | 收藏比赛、联赛、球队 |
| `UserFollow` | user_follows | 关注专家、分析师 |

##### system_models.py - 系统相关

| 模型 | 表名 | 说明 |
|------|------|------|
| `QueryLog` | query_logs | API 查询日志 |
| `ApiToken` | api_tokens | Token 管理 |
| `SystemConfig` | system_config | 系统配置 |

#### 使用示例

```python
from database.server_models.user_models import User
from database.server_models.bet_models import BetRecord
from database.db_core import SelfDB

db = SelfDB()
try:
    # 查询用户
    user = db.query(User).filter(User.username == "admin").first()
    print(f"余额: {user.balance}, 等级: {user.level}")
    
    # 查询投注记录
    bets = db.query(BetRecord).filter(
        BetRecord.user_id == user.id
    ).limit(10).all()
finally:
    db.close()
```

---

## 🔄 导入方式

### 方式1: 从 database/__init__.py 统一导入（推荐）

```python
from database import (
    # 体育数据
    TczqMatch, BjdcMatch, League, Team,
    # 用户相关
    User, UserLevelConfig, UserBalanceLog,
    # 投注相关
    BetRecord, BetOrder,
    # 收藏/关注
    UserFavorite, UserFollow,
    # 系统相关
    QueryLog, ApiToken, SystemConfig,
    # 数据库实例
    datadb, selfdb
)
```

### 方式2: 从子模块直接导入

```python
# 体育数据
from database.data_models import TczqMatch, League

# 用户相关
from database.server_models.user_models import User, UserLevelConfig

# 投注相关
from database.server_models.bet_models import BetRecord, BetOrder

# 收藏/关注
from database.server_models.favorite_models import UserFavorite

# 系统相关
from database.server_models.system_models import QueryLog
```

---

## 📊 数据流向

```
客户端请求
    ↓
FastAPI Router
    ↓
    ├─→ 查询体育数据
    │       ↓
    │   DataDB → data_models/ → soccer_data 数据库
    │
    └─→ 操作用户/投注数据
            ↓
        SelfDB → server_models/ → soccer_server 数据库
```

---

## 🎯 设计优势

### 1. 清晰的职责分离
- **data_models/**: 专注体育数据，只读查询
- **server_models/**: 专注业务逻辑，读写操作

### 2. 模块化组织
- 按功能模块拆分文件（user/bet/favorite/system）
- 每个文件职责单一，易于维护
- 新增功能时只需添加新文件

### 3. 灵活的导入方式
- 支持统一导入（方便）
- 支持按需导入（精确）

### 4. 易于扩展
- 添加新模块：在对应目录下创建新文件
- 添加新表：在对应文件中添加模型类
- 无需修改其他文件

---

## 📝 添加新模型的步骤

### 场景1: 添加体育数据表

1. 在 `data_models/` 中创建或修改文件
2. 定义 SQLAlchemy 模型类
3. 在 `data_models/__init__.py` 中导出
4. 在 `database/__init__.py` 中添加导出

### 场景2: 添加用户相关功能

1. 在 `server_models/user_models.py` 中添加模型
2. 在 `server_models/__init__.py` 中导出
3. 运行 `python init_server_db.py` 创建表

### 场景3: 添加全新模块

1. 在 `server_models/` 中创建新文件（如 `message_models.py`）
2. 定义模型类
3. 在 `server_models/__init__.py` 中导入并导出
4. 在 `database/__init__.py` 中添加导出
5. 更新 `init_server_db.py` 创建表

---

## 🔍 快速查找

### 找用户相关模型？
→ `server_models/user_models.py`

### 找投注记录模型？
→ `server_models/bet_models.py`

### 找比赛数据模型？
→ `data_models/tczq_models.py` 或 `data_models/bjdc_models.py`

### 找联赛/球队模型？
→ `data_models/base_models.py`

---

## 📌 注意事项

1. **Base 声明**: 每个模块文件都独立声明 `Base = declarative_base()`
2. **表名前缀**: 建议使用模块前缀避免冲突（如 `api_users`, `bet_records`）
3. **索引优化**: 为常用查询字段添加 Index
4. **向后兼容**: `database/__init__.py` 保留了旧的全局导出

---

**更新日期**: 2026-04-27  
**版本**: 2.0.0（重构版）
