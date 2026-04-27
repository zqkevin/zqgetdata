# Soccer Data API - 完整接口文档

## 📋 目录

- [概述](#概述)
- [认证机制](#认证机制)
- [接口列表](#接口列表)
  - [健康检查](#1-健康检查)
  - [认证接口](#2-认证接口)
  - [体彩足球](#3-体彩足球接口)
  - [北京单场](#4-北京单场接口)
  - [基础数据](#5-基础数据接口)
- [响应格式](#响应格式)
- [错误码](#错误码)
- [测试说明](#测试说明)

---

## 概述

**Soccer Data API** 是一个基于 FastAPI 构建的体育数据查询服务，提供体彩足球、北京单场等赛事数据的 RESTful API 接口。

### 基本信息

- **基础 URL**: `http://localhost:8000`
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)
- **备用文档**: `http://localhost:8000/redoc` (ReDoc)
- **版本**: 1.0.0

### 技术栈

- **框架**: FastAPI 0.109.0
- **数据库**: MySQL (双数据库架构)
  - `soccer_data` - 体育数据（只读）
  - `soccer_server` - API 服务管理（用户、日志）
- **认证**: JWT (JSON Web Token)

---

## 认证机制

本 API 采用 **JWT Bearer Token** 认证方式。

### 认证流程

1. **登录获取 Token**
   ```bash
   POST /api/auth/login
   Content-Type: application/json
   
   {
     "username": "admin",
     "password": "admin123"
   }
   ```

2. **在请求头中使用 Token**
   ```bash
   Authorization: Bearer <your_token_here>
   ```

### 默认账户

- **用户名**: `admin`
- **密码**: `admin123`

⚠️ **重要**: 生产环境请立即修改默认密码！

---

## 接口列表

### 1. 健康检查

#### GET `/health`

检查服务是否正常运行。

**请求参数**: 无

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-27T06:25:00"
}
```

**状态码**:
- `200` - 服务正常

---

### 2. 认证接口

#### POST `/api/auth/login`

用户登录，获取访问令牌。

**请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**状态码**:
- `200` - 登录成功
- `401` - 用户名或密码错误
- `403` - 账户已禁用

---

#### POST `/api/auth/register`

注册新用户。

**请求体**:
```json
{
  "username": "newuser",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "message": "User created successfully"
}
```

**状态码**:
- `200` - 注册成功
- `400` - 用户名已存在

---

### 3. 体彩足球接口

#### GET `/api/tczq/matches`

查询体彩足球比赛列表。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| issue | string | 否 | 期号筛选 |
| limit | integer | 否 | 返回数量限制 (1-1000, 默认 100) |

**请求示例**:
```bash
GET /api/tczq/matches?limit=10
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "match_id": 2039374,
      "match_num_str": "1009",
      "issue": "2026-04-28",
      "match_time": "2026-04-28T03:15:00",
      "league_name": "亚洲冠军精英联赛",
      "home_team_name": "麦克阿瑟FC",
      "away_team_name": "武里南联",
      "status": 0
    }
  ],
  "total": 10
}
```

**状态码**:
- `200` - 查询成功
- `401` - 未授权

---

#### GET `/api/tczq/match/{match_id}`

查询单场比赛详情（包含赔率）。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| match_id | integer | 比赛 ID |

**请求示例**:
```bash
GET /api/tczq/match/2039374
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "match": {
      "match_id": 2039374,
      "match_num_str": "1009",
      "match_time": "2026-04-28T03:15:00",
      "league_name": "亚洲冠军精英联赛",
      "home_team_name": "麦克阿瑟FC",
      "away_team_name": "武里南联"
    },
    "spf_odds": [
      {
        "company_name": "竞彩官方",
        "home_odds": 1.85,
        "draw_odds": 3.40,
        "away_odds": 4.20
      }
    ],
    "handicap_spf_odds": [],
    "total_goal_odds": [],
    "score_odds": []
  }
}
```

**状态码**:
- `200` - 查询成功
- `404` - 比赛不存在
- `401` - 未授权

---

#### GET `/api/tczq/odds/spf`

查询胜平负赔率。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| match_id | integer | 否 | 比赛 ID |
| company_name | string | 否 | 公司名称筛选 |
| limit | integer | 否 | 返回数量限制 (默认 100) |

**请求示例**:
```bash
GET /api/tczq/odds/spf?match_id=2039374&limit=5
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [...],
  "total": 5
}
```

---

#### GET `/api/tczq/results`

查询比赛结果。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| issue | string | 否 | 期号筛选 |
| limit | integer | 否 | 返回数量限制 (默认 100) |

**请求示例**:
```bash
GET /api/tczq/results?limit=10
Authorization: Bearer <token>
```

---

### 4. 北京单场接口

#### GET `/api/bjdc/matches`

查询北京单场比赛列表。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| issue | string | 否 | 期号筛选 |
| limit | integer | 否 | 返回数量限制 (1-1000, 默认 100) |

**请求示例**:
```bash
GET /api/bjdc/matches?limit=5
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [...],
  "total": 5
}
```

---

#### GET `/api/bjdc/match/{match_id}`

查询北京单场详情。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| match_id | integer | 比赛 ID |

---

#### GET `/api/bjdc/results`

查询北京单场赛果。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| issue | string | 否 | 期号筛选 |
| limit | integer | 否 | 返回数量限制 (默认 100) |

---

### 5. 基础数据接口

#### GET `/api/base/leagues`

查询联赛列表。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| league_name | string | 否 | 联赛名称模糊搜索 |
| limit | integer | 否 | 返回数量限制 (默认 100) |

**请求示例**:
```bash
GET /api/base/leagues?limit=5
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "league_id": 123,
      "league_name": "亚洲冠军精英联赛",
      "league_name_abbr": "亚冠精英",
      "country": "亚洲"
    }
  ],
  "total": 5
}
```

---

#### GET `/api/base/teams`

查询球队列表。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| team_name | string | 否 | 球队名称模糊搜索 |
| limit | integer | 否 | 返回数量限制 (默认 100) |

**请求示例**:
```bash
GET /api/base/teams?limit=5
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "team_id": 456,
      "team_full_name": "麦克阿瑟FC",
      "team_short_name": "麦克阿瑟",
      "country": "澳大利亚"
    }
  ],
  "total": 5
}
```

---

#### GET `/api/base/team/{team_id}/aliases`

查询球队别名。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| team_id | integer | 球队 ID |

**请求示例**:
```bash
GET /api/base/team/456/aliases
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "team_id": 456,
    "team_name": "麦克阿瑟FC",
    "aliases": [
      "Macarthur FC",
      "麦克阿瑟",
      "Macarthur"
    ]
  }
}
```

---

## 响应格式

所有 API 响应遵循统一格式：

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {...},
  "total": 10
}
```

### 错误响应
```json
{
  "detail": "Error message here"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 业务状态码 (200=成功) |
| message | string | 响应消息 |
| data | object/array | 响应数据 |
| total | integer | 总记录数（列表接口） |
| detail | string | 错误详情（错误时） |

---

## 错误码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token 缺失或无效） |
| 403 | 禁止访问（账户禁用等） |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

---

## 测试说明

### 运行自动化测试

项目提供了完整的自动化测试脚本：

```bash
cd api
python test/test_api.py
```

### 测试覆盖范围

测试脚本会自动执行以下测试：

1. ✅ **健康检查** - 验证服务是否正常运行
2. ✅ **管理员登录** - 测试登录接口并获取 Token
3. ✅ **用户注册** - 测试新用户注册功能
4. ✅ **体彩足球比赛列表** - 查询比赛数据
5. ✅ **体彩足球比赛详情** - 查询单场比赛及赔率
6. ✅ **北京单场比赛列表** - 查询 BJDC 比赛
7. ✅ **联赛列表** - 查询基础联赛数据
8. ✅ **球队列表** - 查询基础球队数据
9. ✅ **未授权访问拦截** - 验证安全机制
10. ✅ **无效 Token 拦截** - 验证 Token 验证

### 测试结果示例

```
======================================================================
  测试总结
======================================================================

总测试数: 10
通过: 10 ✅
失败: 0 ❌
通过率: 100.0%

🎉 所有测试通过！
```

### 手动测试

也可以使用 curl 或 Postman 进行手动测试：

```bash
# 1. 登录获取 Token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 使用 Token 查询比赛
curl -X GET "http://localhost:8000/api/tczq/matches?limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 常见问题

### Q1: 如何修改默认管理员密码？

A: 登录后调用注册接口创建新账户，或直接修改数据库中的 `api_users` 表。

### Q2: Token 有效期是多久？

A: 默认 30 分钟，可在 `.env` 中修改 `ACCESS_TOKEN_EXPIRE_MINUTES`。

### Q3: 如何查看 API 文档？

A: 访问 `http://localhost:8000/docs` (Swagger UI) 或 `http://localhost:8000/redoc` (ReDoc)。

### Q4: 为什么有些接口返回空数据？

A: 可能数据库中暂无相关数据，或查询条件过于严格。尝试放宽筛选条件。

### Q5: 如何记录 API 调用日志？

A: 当前版本支持查询日志功能，可在路由中添加日志记录代码（见 DUAL_DATABASE_ARCHITECTURE.md）。

---

## 更新日志

### v1.0.0 (2026-04-27)

- ✅ 初始版本发布
- ✅ 实现双数据库架构
- ✅ 完成 JWT 认证机制
- ✅ 提供体彩足球、北京单场、基础数据接口
- ✅ 添加自动化测试脚本
- ✅ 完善 API 文档

---

**文档版本**: 1.0.0  
**最后更新**: 2026-04-27  
**维护者**: Soccer Data API Team
