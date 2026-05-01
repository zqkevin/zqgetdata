# 体育彩票数据采集系统 - 数据库设计文档

## 📋 目录

- [1. 概述](#1-概述)
- [2. 数据库架构](#2-数据库架构)
- [3. 表结构详解](#3-表结构详解)
  - [3.1 基础数据表（公用）](#31-基础数据表公用)
  - [3.2 体彩足球表（TCZQ）](#32-体彩足球表tczq)
  - [3.3 北京单场表（BJDC）](#33-北京单场表bjdc)
  - [3.4 竞彩篮球表（TCBK）](#34-竞彩篮球表tcbk)
  - [3.5 数字彩表](#35-数字彩表)
- [4. 表关系图](#4-表关系图)
- [5. 索引策略](#5-索引策略)
- [6. 设计规范](#6-设计规范)
- [7. 初始化与维护](#7-初始化与维护)

---

## 1. 概述

### 1.1 数据库基本信息

- **数据库类型**: MySQL 8.0
- **字符集**: utf8mb4
- **排序规则**: utf8mb4_unicode_ci
- **ORM框架**: SQLAlchemy 2.0
- **连接池**: SQLAlchemy Pool (默认配置)

### 1.2 设计原则

1. **多源数据隔离**: TCZQ、BJDC、TCBK 使用独立表前缀，避免数据混淆
2. **公用数据共享**: League、Team、TeamAlias 为所有彩种共用
3. **赔率波动追溯**: 采用累计式记录，保留历史变化轨迹
4. **智能重连机制**: QueryWrapper 自动处理 MySQL 断连（最多重试3次）
5. **零回归原则**: 所有修改不影响现有功能和数据结构

### 1.3 表分类统计

| 分类 | 表数量 | 说明 |
|------|--------|------|
| 基础数据表 | 3 | league, team, team_alias |
| 体彩足球表 | 8 | tczq_match + 5种赔率 + result + odds_log |
| 北京单场表 | 8 | bjdc_match + 5种赔率 + result + odds_log |
| 竞彩篮球表 | 8 | tcbk_league + tcbk_match + 4种赔率 + result + odds_log |
| 数字彩表 | 1 | digital_lottery_draw |
| **总计** | **28** | - |

---

## 2. 数据库架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────┐
│                  基础数据层（公用）                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  league  │  │   team   │  │   team_alias     │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────┘
         ↓              ↓                ↓
┌─────────────────────────────────────────────────────┐
│              业务数据层（按彩种隔离）                   │
│                                                       │
│  ┌──────────────────────────────────────────┐        │
│  │      体彩足球 (TCZQ) - tczq_*            │        │
│  │  match → spf/rqspf/bqc/jqs/sfc/result   │        │
│  └──────────────────────────────────────────┘        │
│                                                       │
│  ┌──────────────────────────────────────────┐        │
│  │      北京单场 (BJDC) - bjdc_*            │        │
│  │  match → spf/rqspf/bqc/jqs/sfc/result   │        │
│  └──────────────────────────────────────────┘        │
│                                                       │
│  ┌──────────────────────────────────────────┐        │
│  │      竞彩篮球 (TCBK) - tcbk_*            │        │
│  │  match → spf/rfsf/dxf/sfc/result        │        │
│  └──────────────────────────────────────────┘        │
│                                                       │
│  ┌──────────────────────────────────────────┐        │
│  │      数字彩 - digital_*                  │        │
│  │  lottery_draw                            │        │
│  └──────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│              日志追踪层（可选）                        │
│  ┌──────────────────────────────────────────┐        │
│  │  *_odds_change_log / bk_odds_change_log  │        │
│  └──────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────┘
```

### 2.2 命名规范

- **表名前缀**: 
  - `tczq_` - 体彩足球
  - `bjdc_` - 北京单场
  - `tcbk_` - 竞彩篮球
  - `digital_` - 数字彩
  - 无前缀 - 基础公用表

- **字段命名**: snake_case（小写+下划线）
- **主键**: 统一使用 `id` (INT, AUTO_INCREMENT)
- **外键**: `{referenced_table}_id`
- **时间字段**: `created_at`, `updated_at`

---

## 3. 表结构详解

### 3.1 基础数据表（公用）

#### 3.1.1 league - 联赛信息表

**用途**: 存储所有彩种共用的联赛基础信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| league_id | INT | UNIQUE, NOT NULL, INDEX | 联赛ID（API返回） |
| league_name | VARCHAR(100) | NOT NULL | 联赛全称 |
| league_name_abbr | VARCHAR(20) | NOT NULL | 联赛简称 |
| region | VARCHAR(50) | - | 联赛地区 |
| country | VARCHAR(50) | - | 联赛国家 |
| href | VARCHAR(255) | NOT NULL | 联赛链接地址 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**索引**:
- PRIMARY KEY (`id`)
- UNIQUE KEY (`league_id`)
- INDEX (`league_id`)

**示例数据**:
```sql
INSERT INTO league (league_id, league_name, league_name_abbr, region, country, href) 
VALUES (1001, '英格兰超级联赛', '英超', '欧洲', '英格兰', 'https://...');
```

---

#### 3.1.2 team - 球队信息表

**用途**: 存储所有彩种共用的球队基础信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| team_id | INT | UNIQUE, NOT NULL, INDEX | 球队ID（API返回） |
| team_code | VARCHAR(20) | NOT NULL | 球队代码 |
| team_full_name | VARCHAR(100) | NOT NULL | 球队全称 |
| team_short_name | VARCHAR(20) | NOT NULL | 球队简称 |
| team_short_en_name | VARCHAR(20) | - | 球队英文简称 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**索引**:
- PRIMARY KEY (`id`)
- UNIQUE KEY (`team_id`)
- INDEX (`team_id`)

**关系**:
- 一对多: `team` → `team_alias` (通过 `team_id` 关联)

**示例数据**:
```sql
INSERT INTO team (team_id, team_code, team_full_name, team_short_name, team_short_en_name) 
VALUES (5001, 'MUN', '曼彻斯特联队', '曼联', 'Man Utd');
```

---

#### 3.1.3 team_alias - 球队别名字典表

**用途**: 存储同一球队在不同数据源的别名，用于跨系统匹配

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| team_id | INT | FK → team.id, NOT NULL | 关联球队ID |
| alias_name | VARCHAR(100) | NOT NULL | 别名名称 |
| source_type | VARCHAR(20) | NOT NULL | 来源类型 (tczq/bjdc/okooo等) |
| is_primary | INT | DEFAULT 0 | 是否为主别名 (1=是, 0=否) |
| remark | TEXT | - | 备注说明 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

**索引**:
- PRIMARY KEY (`id`)
- FOREIGN KEY (`team_id`) REFERENCES `team(id)`

**示例数据**:
```sql
-- 曼联在不同系统的别名
INSERT INTO team_alias (team_id, alias_name, source_type, is_primary) VALUES 
(1, '曼联', 'tczq', 1),
(1, '曼彻斯特联', 'bjdc', 0),
(1, 'Man United', 'okooo', 0);
```

**应用场景**:
- TCZQ API 返回 "曼联" → 匹配到 team_id=1
- BJDC API 返回 "曼彻斯特联" → 通过别名匹配到 team_id=1
- 实现跨系统球队统一标识

---

### 3.2 体彩足球表（TCZQ）

#### 3.2.1 tczq_match - 体彩足球比赛主表

**用途**: 存储体彩足球比赛的基本信息和状态

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | UNIQUE, NOT NULL, INDEX | 比赛ID（API返回） |
| match_num | INT | - | 比赛编号 |
| match_num_str | VARCHAR(20) | - | 比赛编号字符串（如"周一001"） |
| match_num_date | VARCHAR(10) | - | 比赛日期编号 |
| match_week | VARCHAR(10) | - | 比赛星期 |
| match_date | VARCHAR(20) | - | 比赛日期 |
| match_time | VARCHAR(20) | - | 比赛时间 |
| business_date | VARCHAR(20) | - | 业务日期 |
| league_id | INT | FK → league.league_id | 联赛ID |
| home_team_id | INT | - | 主队ID |
| home_team_code | VARCHAR(20) | - | 主队代码 |
| home_team_all_name | VARCHAR(50) | - | 主队全称 |
| home_team_abb_name | VARCHAR(20) | - | 主队简称 |
| home_team_rank | VARCHAR(20) | - | 主队排名 |
| away_team_id | INT | - | 客队ID |
| away_team_code | VARCHAR(20) | - | 客队代码 |
| away_team_all_name | VARCHAR(50) | - | 客队全称 |
| away_team_abb_name | VARCHAR(20) | - | 客队简称 |
| away_team_rank | VARCHAR(20) | - | 客队排名 |
| base_home_team_id | INT | - | 基础主队ID（关联team表） |
| base_away_team_id | INT | - | 基础客队ID（关联team表） |
| match_name | VARCHAR(50) | - | 比赛名称 |
| group_name | VARCHAR(50) | - | 分组名称 |
| match_status | INT | DEFAULT 0 | 比赛状态 (0=待开赛, 1=进行中, 2=延期, 3=取消, 8=已完成) |
| sell_status | INT | - | 销售状态 |
| is_hot | INT | - | 是否热门 |
| is_hide | INT | - | 是否隐藏 |
| betting_single | INT | - | 单场投注 |
| betting_all_up | INT | - | 串关投注 |
| back_color | VARCHAR(20) | - | 背景颜色 |
| remark | TEXT | - | 备注 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**索引**:
- PRIMARY KEY (`id`)
- UNIQUE KEY (`match_id`)
- INDEX (`match_id`)
- FOREIGN KEY (`league_id`) REFERENCES `league(league_id)`

**比赛状态码**:
```python
MATCH_STATUS = {
    0: '待开赛',
    1: '进行中',
    2: '延期',
    3: '取消',
    8: '已完成'
}
```

**关系**:
- 一对一: `tczq_match` → `tczq_spf`
- 一对一: `tczq_match` → `tczq_rqspf`
- 一对一: `tczq_match` → `tczq_bqc`
- 一对一: `tczq_match` → `tczq_jqs`
- 一对一: `tczq_match` → `tczq_sfc`
- 一对一: `tczq_match` → `tczq_result`
- 一对多: `tczq_match` → `tczq_odds_change_log`

---

#### 3.2.2 tczq_spf - 胜平负赔率表

**用途**: 存储体彩足球胜平负玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tczq_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| win_pl | FLOAT | DEFAULT 0 | 主队胜赔率 |
| draw_pl | FLOAT | DEFAULT 0 | 平局赔率 |
| lose_pl | FLOAT | DEFAULT 0 | 客队胜赔率 |
| winpl_eu | FLOAT | DEFAULT 0 | 欧洲平均胜赔率 |
| drawpl_eu | FLOAT | DEFAULT 0 | 欧洲平均平赔率 |
| losepl_eu | FLOAT | DEFAULT 0 | 欧洲平均负赔率 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**索引**:
- PRIMARY KEY (`id`)
- UNIQUE KEY (`match_id`)
- FOREIGN KEY (`match_id`) REFERENCES `tczq_match(match_id)`

**示例数据**:
```sql
INSERT INTO tczq_spf (match_id, win_pl, draw_pl, lose_pl, winpl_eu, drawpl_eu, losepl_eu) 
VALUES (12345, 2.15, 3.20, 3.10, 2.10, 3.25, 3.15);
```

---

#### 3.2.3 tczq_rqspf - 让球胜平负赔率表

**用途**: 存储体彩足球让球胜平负玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tczq_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| handicap | FLOAT | DEFAULT 0 | 让球数（正数=主队让球，负数=客队让球） |
| win_pl | FLOAT | DEFAULT 0 | 让球胜赔率 |
| draw_pl | FLOAT | DEFAULT 0 | 让球平赔率 |
| lose_pl | FLOAT | DEFAULT 0 | 让球负赔率 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**让球数说明**:
- `handicap = -1`: 主队让1球
- `handicap = +1`: 客队让1球（主队受让1球）
- `handicap = 0`: 不让球

---

#### 3.2.4 tczq_bqc - 半全场胜平负赔率表

**用途**: 存储体彩足球半全场胜平负玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tczq_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| half_win_full_win | FLOAT | DEFAULT 0 | 半场胜全场胜 |
| half_win_full_draw | FLOAT | DEFAULT 0 | 半场胜全场平 |
| half_win_full_lose | FLOAT | DEFAULT 0 | 半场胜全场负 |
| half_draw_full_win | FLOAT | DEFAULT 0 | 半场平全场胜 |
| half_draw_full_draw | FLOAT | DEFAULT 0 | 半场平全场平 |
| half_draw_full_lose | FLOAT | DEFAULT 0 | 半场平全场负 |
| half_lose_full_win | FLOAT | DEFAULT 0 | 半场负全场胜 |
| half_lose_full_draw | FLOAT | DEFAULT 0 | 半场负全场平 |
| half_lose_full_lose | FLOAT | DEFAULT 0 | 半场负全场负 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**9种组合**:
1. 胜胜 (half_win_full_win)
2. 胜平 (half_win_full_draw)
3. 胜负 (half_win_full_lose)
4. 平胜 (half_draw_full_win)
5. 平平 (half_draw_full_draw)
6. 平负 (half_draw_full_lose)
7. 负胜 (half_lose_full_win)
8. 负平 (half_lose_full_draw)
9. 负负 (half_lose_full_lose)

---

#### 3.2.5 tczq_jqs - 总进球赔率表

**用途**: 存储体彩足球总进球数玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tczq_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| goal_0 | FLOAT | DEFAULT 0 | 总进球0个 |
| goal_1 | FLOAT | DEFAULT 0 | 总进球1个 |
| goal_2 | FLOAT | DEFAULT 0 | 总进球2个 |
| goal_3 | FLOAT | DEFAULT 0 | 总进球3个 |
| goal_4 | FLOAT | DEFAULT 0 | 总进球4个 |
| goal_5 | FLOAT | DEFAULT 0 | 总进球5个 |
| goal_6 | FLOAT | DEFAULT 0 | 总进球6个 |
| goal_about | FLOAT | DEFAULT 0 | 总进球7+个 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

---

#### 3.2.6 tczq_sfc - 比分赔率表

**用途**: 存储体彩足球比分玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tczq_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| score_0_0 ~ score_7_0 | FLOAT | DEFAULT 0 | 各比分赔率（共31个字段） |
| score_win_about | FLOAT | DEFAULT 0 | 胜其他 |
| score_lose_about | FLOAT | DEFAULT 0 | 负其他 |
| score_draw_about | FLOAT | DEFAULT 0 | 平其他 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**比分字段列表** (31个):
- 0:0, 0:1, 0:2, 0:3, 0:4, 0:5
- 1:0, 1:1, 1:2, 1:3, 1:4, 1:5
- 2:0, 2:1, 2:2, 2:3, 2:4, 2:5
- 3:0, 3:1, 3:2, 3:3, 3:4, 3:5
- 4:0, 4:1, 4:2, 4:3, 4:4, 4:5
- 5:0, 5:1, 5:2
- 6:0, 6:1
- 7:0
- 胜其他、负其他、平其他

---

#### 3.2.7 tczq_result - 体彩足球赛果表

**用途**: 存储体彩足球比赛的最终赛果

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tczq_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| home_team_goals | INT | DEFAULT 0 | 主队全场得分 |
| away_team_goals | INT | DEFAULT 0 | 客队全场得分 |
| half_time_home_goals | INT | DEFAULT 0 | 主队半场得分 |
| half_time_away_goals | INT | DEFAULT 0 | 客队半场得分 |
| result_type | VARCHAR(10) | - | 赛果类型 (胜/平/负) |
| handicap_result | VARCHAR(10) | - | 让球赛果 |
| total_goals | INT | DEFAULT 0 | 总进球数 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**示例数据**:
```sql
INSERT INTO tczq_result (match_id, home_team_goals, away_team_goals, 
                         half_time_home_goals, half_time_away_goals,
                         result_type, handicap_result, total_goals) 
VALUES (12345, 2, 1, 1, 0, '胜', '胜', 3);
```

---

#### 3.2.8 tczq_odds_change_log - 体彩足球赔率变化日志表

**用途**: 累计记录体彩足球赔率的每次变化（非覆盖式）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | NOT NULL, INDEX | 比赛ID |
| odds_table | VARCHAR(50) | NOT NULL | 赔率表名 (如 tczq_spf) |
| odds_record_id | INT | NOT NULL, INDEX | 赔率记录ID (关联具体赔率表主键) |
| odds_field | VARCHAR(50) | NOT NULL | 赔率字段 (如 win_pl) |
| old_value | FLOAT | NOT NULL | 旧值 |
| new_value | FLOAT | NOT NULL | 新值 |
| change_time | DATETIME | NOT NULL | 变化时间 |
| created_at | DATETIME | DEFAULT NOW() | 记录创建时间 |

**索引**:
- PRIMARY KEY (`id`)
- INDEX (`match_id`)
- INDEX (`odds_record_id`)

**设计优势**:
- ✅ 保留完整的历史变化轨迹
- ✅ 可分析赔率波动趋势
- ✅ 支持回滚和审计

**示例数据**:
```sql
INSERT INTO tczq_odds_change_log 
(match_id, odds_table, odds_record_id, odds_field, old_value, new_value, change_time) 
VALUES 
(12345, 'tczq_spf', 100, 'win_pl', 2.15, 2.20, '2026-04-24 10:30:00'),
(12345, 'tczq_spf', 100, 'win_pl', 2.20, 2.18, '2026-04-24 11:00:00');
```

---

### 3.3 北京单场表（BJDC）

> **说明**: BJDC表结构与TCZQ完全一致，仅表名前缀不同
> - `bjdc_match` - 比赛主表
> - `bjdc_spf` - 胜平负赔率
> - `bjdc_rqspf` - 让球胜平负赔率
> - `bjdc_bqc` - 半全场胜平负赔率
> - `bjdc_jqs` - 总进球赔率
> - `bjdc_sfc` - 比分赔率
> - `bjdc_result` - 赛果表
> - `bjdc_odds_change_log` - 赔率变化日志

**关键区别**:
- TCZQ 和 BJDC 的 `match_id` 可能相同，但代表不同的比赛
- 两个系统独立运行，互不干扰
- 通过 `team_alias` 表实现球队统一标识

---

### 3.4 竞彩篮球表（TCBK）

#### 3.4.1 tcbk_league - 竞彩篮球联赛表

**用途**: 存储竞彩篮球专用的联赛信息（与football的league表独立）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| league_id | INT | UNIQUE, NOT NULL, INDEX | 联赛ID |
| league_name | VARCHAR(50) | NOT NULL | 联赛全称 |
| league_name_abbr | VARCHAR(20) | NOT NULL | 联赛简称 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**注意**: TCBK 使用独立的联赛表，不与 football 共用

---

#### 3.4.2 tcbk_match - 竞彩篮球比赛主表

**用途**: 存储竞彩篮球比赛的基本信息和状态

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | UNIQUE, NOT NULL, INDEX | 比赛ID |
| match_num | INT | - | 比赛编号 |
| match_num_str | VARCHAR(20) | - | 比赛编号字符串 |
| match_num_date | VARCHAR(10) | - | 比赛日期编号 |
| match_week | VARCHAR(10) | - | 比赛星期 |
| match_date | VARCHAR(20) | - | 比赛日期 |
| match_time | VARCHAR(20) | - | 比赛时间 |
| business_date | VARCHAR(20) | - | 业务日期 |
| league_id | INT | FK → tcbk_league.league_id | 联赛ID |
| home_team_id | INT | - | 主队ID |
| home_team_code | VARCHAR(20) | - | 主队代码 |
| home_team_all_name | VARCHAR(50) | - | 主队全称 |
| home_team_abb_name | VARCHAR(20) | - | 主队简称 |
| home_team_rank | VARCHAR(20) | - | 主队排名 |
| away_team_id | INT | - | 客队ID |
| away_team_code | VARCHAR(20) | - | 客队代码 |
| away_team_all_name | VARCHAR(50) | - | 客队全称 |
| away_team_abb_name | VARCHAR(20) | - | 客队简称 |
| away_team_rank | VARCHAR(20) | - | 客队排名 |
| base_home_team_id | INT | - | 基础主队ID |
| base_away_team_id | INT | - | 基础客队ID |
| match_name | VARCHAR(50) | - | 比赛名称 |
| group_name | VARCHAR(50) | - | 分组名称 |
| match_status | INT | DEFAULT 0 | 比赛状态 (0=待开赛, 1=进行中, 2=延期, 3=取消, 8=已完成) |
| sell_status | INT | - | 销售状态 |
| is_hot | INT | - | 是否热门 |
| is_hide | INT | - | 是否隐藏 |
| betting_single | INT | - | 单场投注 |
| betting_all_up | INT | - | 串关投注 |
| back_color | VARCHAR(20) | - | 背景颜色 |
| remark | TEXT | - | 备注 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**关系**:
- 一对一: `tcbk_match` → `tcbk_spf`
- 一对一: `tcbk_match` → `tcbk_rfsf`
- 一对一: `tcbk_match` → `tcbk_dxf`
- 一对一: `tcbk_match` → `tcbk_sfc`
- 一对一: `tcbk_match` → `tcbk_result`
- 一对多: `tcbk_match` → `bk_odds_change_log`

---

#### 3.4.3 tcbk_spf - 胜负赔率表

**用途**: 存储竞彩篮球胜负玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tcbk_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| h | FLOAT | - | 主队胜赔率 |
| a | FLOAT | - | 客队胜赔率 |
| hf | INT | - | 主队胜赔率变化标识 |
| af | INT | - | 客队胜赔率变化标识 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| update_time | DATETIME | ON UPDATE NOW() | 更新时间 |

**篮球特有字段**:
- `hf`, `af`: 赔率变化标识（1=上升，-1=下降，0=不变）

---

#### 3.4.4 tcbk_rfsf - 让分胜负赔率表

**用途**: 存储竞彩篮球让分胜负玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tcbk_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| goal_line | FLOAT | - | 让分数值 |
| goal_line_str | VARCHAR(10) | - | 让分数值字符串 |
| h | FLOAT | - | 主队胜赔率 |
| a | FLOAT | - | 客队胜赔率 |
| hf | INT | - | 主队胜赔率变化标识 |
| af | INT | - | 客队胜赔率变化标识 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| update_time | DATETIME | ON UPDATE NOW() | 更新时间 |

**让分数值说明**:
- `goal_line = -5.5`: 主队让5.5分
- `goal_line = +5.5`: 客队让5.5分（主队受让5.5分）

---

#### 3.4.5 tcbk_dxf - 大小分赔率表

**用途**: 存储竞彩篮球大小分玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tcbk_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| goal_line | FLOAT | - | 大小分盘口 |
| goal_line_str | VARCHAR(10) | - | 大小分盘口字符串 |
| over | FLOAT | - | 大分赔率 |
| under | FLOAT | - | 小分赔率 |
| overf | INT | - | 大分赔率变化标识 |
| underf | INT | - | 小分赔率变化标识 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| update_time | DATETIME | ON UPDATE NOW() | 更新时间 |

---

#### 3.4.6 tcbk_sfc - 胜分差赔率表

**用途**: 存储竞彩篮球胜分差玩法的赔率数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tcbk_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| h1 ~ h6 | FLOAT | - | 主队胜1-5分 ~ 主队胜26+分 |
| a1 ~ a6 | FLOAT | - | 客队胜1-5分 ~ 客队胜26+分 |
| h1f ~ h6f | INT | - | 主队各档位赔率变化标识 |
| a1f ~ a6f | INT | - | 客队各档位赔率变化标识 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| update_time | DATETIME | ON UPDATE NOW() | 更新时间 |

**12种分差档位**:
- 主队胜: 1-5分, 6-10分, 11-15分, 16-20分, 21-25分, 26+分
- 客队胜: 1-5分, 6-10分, 11-15分, 16-20分, 21-25分, 26+分

---

#### 3.4.7 tcbk_result - 竞彩篮球赛果表

**用途**: 存储竞彩篮球比赛的最终赛果

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| match_id | INT | FK → tcbk_match.match_id, UNIQUE, NOT NULL | 比赛ID |
| home_team_score | INT | DEFAULT 0 | 主队得分 |
| away_team_score | INT | DEFAULT 0 | 客队得分 |
| half_time_home_score | INT | DEFAULT 0 | 主队半场得分 |
| half_time_away_score | INT | DEFAULT 0 | 客队半场得分 |
| result_type | VARCHAR(10) | - | 赛果类型 (主胜/客胜) |
| rfsf_result | VARCHAR(10) | - | 让分赛果 |
| dxf_result | VARCHAR(10) | - | 大小分赛果 |
| sfc_result | VARCHAR(10) | - | 胜分差结果 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

---

#### 3.4.8 bk_odds_change_log - 竞彩篮球赔率变化日志表

**用途**: 累计记录竞彩篮球赔率的每次变化

> 表结构与 `tczq_odds_change_log` 相同，仅表名不同

---

### 3.5 数字彩表

#### 3.5.1 digital_lottery_draw - 数字彩开奖表

**用途**: 存储数字彩（双色球、大乐透等）的开奖数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AI | 自增主键 |
| lottery_type | VARCHAR(20) | NOT NULL | 彩种类型 (ssq/dlt/3d/pl3/pl5等) |
| draw_number | VARCHAR(20) | NOT NULL | 期号 |
| draw_date | DATE | NOT NULL | 开奖日期 |
| red_balls | VARCHAR(50) | - | 红球号码（逗号分隔） |
| blue_balls | VARCHAR(50) | - | 蓝球号码（逗号分隔） |
| front_zone | VARCHAR(50) | - | 前区号码（大乐透） |
| back_zone | VARCHAR(50) | - | 后区号码（大乐透） |
| prize_pool | DECIMAL(15,2) | - | 奖池金额 |
| first_prize_count | INT | - | 一等奖注数 |
| first_prize_amount | DECIMAL(10,2) | - | 一等奖单注金额 |
| sales_amount | DECIMAL(15,2) | - | 销售额 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

**彩种类型**:
- `ssq`: 双色球
- `dlt`: 大乐透
- `3d`: 福彩3D
- `pl3`: 排列三
- `pl5`: 排列五

**示例数据**:
```sql
-- 双色球
INSERT INTO digital_lottery_draw 
(lottery_type, draw_number, draw_date, red_balls, blue_balls, first_prize_count, first_prize_amount) 
VALUES ('ssq', '2026045', '2026-04-23', '01,05,12,18,25,30', '08', 5, 8500000.00);

-- 大乐透
INSERT INTO digital_lottery_draw 
(lottery_type, draw_number, draw_date, front_zone, back_zone) 
VALUES ('dlt', '2026045', '2026-04-23', '03,08,15,22,29', '04,11');
```

---

## 4. 表关系图

### 4.1 基础数据关系

```
┌──────────────┐       ┌──────────────────┐
│   league     │       │      team        │
├──────────────┤       ├──────────────────┤
│ id (PK)      │       │ id (PK)          │
│ league_id    │       │ team_id          │
│ league_name  │       │ team_code        │
│ ...          │       │ team_full_name   │
└──────────────┘       │ ...              │
                       └────────┬─────────┘
                                │ 1:N
                       ┌────────▼─────────┐
                       │   team_alias     │
                       ├──────────────────┤
                       │ id (PK)          │
                       │ team_id (FK)     │
                       │ alias_name       │
                       │ source_type      │
                       └──────────────────┘
```

### 4.2 TCZQ/BJDC 关系

```
┌──────────────────┐
│  tczq_match      │ ← league_id (FK → league.league_id)
├──────────────────┤
│ id (PK)          │
│ match_id         │
│ home_team_id     │ ← 通过 team_alias 匹配
│ away_team_id     │ ← 通过 team_alias 匹配
│ ...              │
└────┬────────┬────┘
     │ 1:1    │ 1:1
┌────▼────┐ ┌─▼──────────┐
│tczq_spf │ │tczq_rqspf  │
└─────────┘ └────────────┘
     │ 1:1         │ 1:1
┌────▼────┐ ┌─▼──────────┐
│tczq_bqc │ │tczq_jqs    │
└─────────┘ └────────────┘
     │ 1:1
┌────▼────┐
│tczq_sfc │
└────┬────┘
     │ 1:1
┌────▼────────┐
│tczq_result  │
└─────────────┘

┌──────────────────────┐
│ tczq_odds_change_log │ ← 1:N 关系
├──────────────────────┤
│ match_id             │
│ odds_table           │
│ odds_record_id (FK)  │
│ odds_field           │
│ old_value            │
│ new_value            │
└──────────────────────┘
```

### 4.3 TCBK 关系

```
┌──────────────────┐
│  tcbk_league     │
├──────────────────┤
│ id (PK)          │
│ league_id        │
└────┬─────────────┘
     │ 1:N
┌────▼─────────────┐
│  tcbk_match      │
├──────────────────┤
│ id (PK)          │
│ match_id         │
│ league_id (FK)   │
└────┬────────┬────┘
     │ 1:1    │ 1:1
┌────▼────┐ ┌─▼──────────┐
│tcbk_spf │ │tcbk_rfsf   │
└─────────┘ └────────────┘
     │ 1:1         │ 1:1
┌────▼────┐ ┌─▼──────────┐
│tcbk_dxf │ │tcbk_sfc    │
└─────────┘ └────────────┘
     │ 1:1
┌────▼────────┐
│tcbk_result  │
└─────────────┘

┌──────────────────────┐
│ bk_odds_change_log   │ ← 1:N 关系
└──────────────────────┘
```

---

## 5. 索引策略

### 5.1 主键索引

所有表均使用 `id INT AUTO_INCREMENT` 作为主键

### 5.2 唯一索引

| 表名 | 字段 | 说明 |
|------|------|------|
| league | league_id | 防止联赛重复 |
| team | team_id | 防止球队重复 |
| *_match | match_id | 防止比赛重复 |
| *_spf, *_rqspf, etc. | match_id | 一场比赛一条赔率记录 |
| *_result | match_id | 一场比赛一个赛果 |

### 5.3 普通索引

| 表名 | 字段 | 用途 |
|------|------|------|
| *_match | match_id | 加速查询 |
| *_odds_change_log | match_id | 按比赛查日志 |
| *_odds_change_log | odds_record_id | 按赔率记录查日志 |

### 5.4 外键索引

| 外键字段 | 引用表 | 说明 |
|----------|--------|------|
| tczq_match.league_id | league.league_id | 联赛关联 |
| bjdc_match.league_id | league.league_id | 联赛关联 |
| tcbk_match.league_id | tcbk_league.league_id | 篮球联赛关联 |
| team_alias.team_id | team.id | 球队别名关联 |
| *_spf.match_id | *_match.match_id | 赔率关联 |
| *_result.match_id | *_match.match_id | 赛果关联 |

---

## 6. 设计规范

### 6.1 数据类型选择

| 数据类型 | 使用场景 | 示例 |
|----------|----------|------|
| INT | ID、状态码、计数 | match_id, match_status |
| VARCHAR(n) | 短文本 | team_code, result_type |
| FLOAT | 赔率、数值 | win_pl, goal_line |
| DECIMAL(15,2) | 金额 | prize_pool, sales_amount |
| TEXT | 长文本、备注 | remark |
| DATETIME | 时间戳 | created_at, change_time |
| DATE | 日期 | draw_date |

### 6.2 默认值规范

- **数值字段**: `DEFAULT 0`
- **字符串字段**: 不设默认值或 `DEFAULT ''`
- **时间字段**: `DEFAULT NOW()` 或 `DEFAULT CURRENT_TIMESTAMP`
- **更新字段**: `ON UPDATE NOW()`

### 6.3 NULL 值处理

- **必填字段**: `NOT NULL`
- **可选字段**: 允许 `NULL`
- **赛果字段**: 允许 `NULL`（未开赛时无赛果）

### 6.4 编码规范

- **数据库**: `utf8mb4`
- **排序规则**: `utf8mb4_unicode_ci`
- **支持**: 中文、emoji等特殊字符

---

## 7. 初始化与维护

### 7.1 数据库初始化

#### 方式一：增量初始化（推荐）

```bash
# 启动程序时自动检测并创建缺失表
python main.py
```

程序会自动：
1. 检查28个必需表是否存在
2. 缺失则调用 `init_restructured_database()`
3. 仅创建不存在的表，保留现有数据

#### 方式二：完全重建（谨慎使用）

```bash
# 删除所有表并重新创建（会清空所有数据！）
python main.py --rebuild
```

⚠️ **警告**: 此操作会删除所有数据，仅在新环境或测试时使用

### 7.2 手动初始化脚本

```python
# app/common/init_restructured_db.py
from app.common.init_restructured_db import init_restructured_database

success = init_restructured_database()
if success:
    print("✅ 数据库初始化成功")
else:
    print("❌ 数据库初始化失败")
```

### 7.3 数据库备份

```bash
# 备份整个数据库
mysqldump -u soccer_data -p soccer_data > backup_$(date +%Y%m%d).sql

# 备份指定表
mysqldump -u soccer_data -p soccer_data tczq_match tczq_result > tczq_backup.sql
```

### 7.4 数据清理

```sql
-- 清理30天前的赔率变化日志
DELETE FROM tczq_odds_change_log 
WHERE change_time < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- 清理已完成的比赛（保留最近90天）
DELETE FROM tczq_match 
WHERE match_status = 8 
  AND match_date < DATE_SUB(CURDATE(), INTERVAL 90 DAY);
```

### 7.5 性能优化建议

1. **定期清理日志表**: `*_odds_change_log` 增长较快，建议定期归档
2. **添加复合索引**: 根据查询模式添加合适的复合索引
3. **分区表**: 对于大数据量表（如match表），可按日期分区
4. **读写分离**: 高并发场景下考虑主从复制

### 7.6 监控指标

| 指标 | 阈值 | 说明 |
|------|------|------|
| 表行数增长率 | < 10%/天 | 异常增长需排查 |
| 查询响应时间 | < 100ms | 慢查询需优化 |
| 连接池使用率 | < 80% | 过高需扩容 |
| 磁盘使用率 | < 70% | 及时清理或扩容 |

---

## 附录

### A. 常用查询示例

#### A.1 查询今日比赛

```sql
SELECT m.match_id, m.match_name, m.match_time, 
       l.league_name,
       h.team_full_name AS home_team,
       a.team_full_name AS away_team
FROM tczq_match m
JOIN league l ON m.league_id = l.league_id
LEFT JOIN team h ON m.base_home_team_id = h.team_id
LEFT JOIN team a ON m.base_away_team_id = a.team_id
WHERE m.match_date = CURDATE()
ORDER BY m.match_time;
```

#### A.2 查询赔率变化历史

```sql
SELECT ocl.change_time, ocl.odds_field, 
       ocl.old_value, ocl.new_value,
       (ocl.new_value - ocl.old_value) AS change_amount
FROM tczq_odds_change_log ocl
WHERE ocl.match_id = 12345
  AND ocl.odds_table = 'tczq_spf'
  AND ocl.odds_field = 'win_pl'
ORDER BY ocl.change_time DESC;
```

#### A.3 统计各联赛比赛数量

```sql
SELECT l.league_name, COUNT(m.id) AS match_count
FROM tczq_match m
JOIN league l ON m.league_id = l.league_id
GROUP BY l.league_name
ORDER BY match_count DESC
LIMIT 10;
```

### B. 常见问题

#### Q1: 为什么TCZQ和BJDC要分开建表？

**A**: 
- 两个系统的 `match_id` 可能相同但代表不同比赛
- 业务逻辑独立，避免数据混淆
- 便于单独维护和扩展

#### Q2: 如何处理球队名称不一致的问题？

**A**: 使用 `team_alias` 表维护别名映射
```sql
-- 查询某球队的所有别名
SELECT ta.alias_name, ta.source_type
FROM team_alias ta
JOIN team t ON ta.team_id = t.id
WHERE t.team_full_name = '曼彻斯特联队';
```

#### Q3: 赔率变化日志会不会太大？

**A**: 
- 建议定期归档（如保留最近3个月）
- 可按月份分表存储
- 只记录关键赔率字段的变化

#### Q4: 如何保证数据一致性？

**A**: 
- 使用事务确保原子性
- 外键约束保证引用完整性
- QueryWrapper 自动重连机制处理断连

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0 | 2026-04-24 | 初始版本，完成28个表的详细文档 |

---

**文档维护者**: 开发团队  
**最后更新**: 2026-04-24  
**联系方式**: zqkevin@163.com
