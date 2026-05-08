# 标准化足球数据库 (Standard Football Database)

## 项目说明

这是一个**完全独立**的项目，用于从 football-data.org API 获取并建立标准化的足球基础数据。

### 项目目标

建立一个标准化的足球名称表，包括：
- 🌍 **国家/地区** (Countries)
- 🏆 **联赛信息** (Leagues) - 包括联赛级别
- ⚽ **球队信息** (Teams) - 标准队名、简称、缩写
- 👥 **主要队员** (Players) - 球员姓名、位置、国籍
- 👔 **教练信息** (Coaches)

### 重要说明

❌ **不包含**: 比赛数据、比分、赛程等动态数据  
✅ **只包含**: 静态的基础参考数据（国家、联赛、球队、球员）

**独立性**: 此项目与现有的 zqgetdata 项目完全独立，不共享任何代码或数据。

## 已获取的数据

### 数据统计 (2026-05-05)

- **国家/地区**: 272 个
- **联赛**: 13 个主要国际联赛
- **球队**: 331 支
- **球员**: 9,757 名
- **平均每队球员数**: 29.5 人

### 覆盖的联赛

#### 主数据源 (football-data.org) - 13个联赛

| 代码 | 联赛名称 | 国家/地区 |
|------|---------|----------|
| BSA | Campeonato Brasileiro Série A | 巴西 |
| ELC | Championship | 英格兰 |
| PL | Premier League | 英格兰 |
| CL | UEFA Champions League | 欧洲 |
| EC | European Championship | 欧洲 |
| FL1 | Ligue 1 | 法国 |
| BL1 | Bundesliga | 德国 |
| SA | Serie A | 意大利 |
| DED | Eredivisie | 荷兰 |
| PPL | Primeira Liga | 葡萄牙 |
| CLI | Copa Libertadores | 南美 |
| PD | Primera Division | 西班牙 |
| WC | FIFA World Cup | 世界 |

#### 扩展数据源 (手动维护) - 4个联赛

| 代码 | 联赛名称 | 国家/地区 | 状态 |
|------|---------|----------|------|
| J1 | J1 League | 日本 | ✅ 已添加 |
| KL1 | K League 1 | 韩国 | ✅ 已添加 |
| SPL | Saudi Pro League | 沙特阿拉伯 | ✅ 已添加 |
| CSL | Chinese Super League | 中国 | ✅ 已添加 |

**注意**: 扩展联赛的球队数据正在逐步添加中。详见 `docs/EXTENDED_DATA_SOLUTIONS.md`

### 数据结构

#### 1. 国家/地区 (countries.json)
```json
{
  "id": 2072,
  "name": "England",
  "code": "ENG",
  "flag": "https://...",
  "parent_area_id": 2077,
  "parent_area_name": "Europe"
}
```

#### 2. 联赛 (leagues.json)
```json
{
  "id": 2021,
  "name": "Premier League",
  "code": "PL",
  "type": "LEAGUE",
  "emblem": "https://...",
  "area_id": 2072,
  "area_name": "England",
  "current_season": {
    "start_date": "2025-08-15",
    "end_date": "2026-05-24",
    "current_matchday": 14
  }
}
```

#### 3. 球队和球员 (teams_with_players.json)
```json
{
  "id": 57,
  "name": "Arsenal FC",
  "short_name": "Arsenal",
  "tla": "ARS",
  "crest": "https://...",
  "founded": 1886,
  "venue": "Emirates Stadium",
  "website": "http://www.arsenal.com",
  "club_colors": "Red / White",
  "league_code": "PL",
  "coach": {
    "id": 12345,
    "name": "Mikel Arteta",
    "nationality": "Spain",
    "contract_start": "2019-12-20",
    "contract_until": "2025-06-30"
  },
  "players": [
    {
      "id": 67890,
      "name": "Bukayo Saka",
      "first_name": "Bukayo",
      "last_name": "Saka",
      "date_of_birth": "2001-09-05",
      "nationality": "England",
      "position": "Midfield",
      "shirt_number": 7
    }
  ]
}
```

- **API 版本**: v4
- **Base URL**: `https://api.football-data.org/v4`
- **认证方式**: HTTP Header `X-Auth-Token`
- **Token**: `b95b11f44dde401bb5f8de79364f59c6` (kevin 的账户)

## 速率限制

根据测试结果，免费账户的限制：
- **每分钟请求数**: 约 10 次/分钟
- **可用竞赛**: 13 个主要联赛
- **信用额度**: 未显示具体限制

## 可获取的数据

### 1. 竞赛 (Competitions) ✅

**数量**: 13 个竞赛

**覆盖国家/地区**:
- 🇧🇷 Brazil: BSA (巴甲)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England: ELC (英冠), PL (英超)
- 🇪🇺 Europe: CL (欧冠), EC (欧洲杯)
- 🇫🇷 France: FL1 (法甲)
- 🇩🇪 Germany: BL1 (德甲)
- 🇮🇹 Italy: SA (意甲)
- 🇳🇱 Netherlands: DED (荷甲)
- 🇵🇹 Portugal: PPL (葡超)
- 🌎 South America: CLI (解放者杯)
- 🇪🇸 Spain: PD (西甲)
- 🌍 World: WC (世界杯)

**数据结构**:
```json
{
  "id": 2021,
  "name": "Premier League",
  "code": "PL",
  "type": "LEAGUE",
  "emblem": "https://crests.football-data.org/PL.png",
  "area": {
    "id": 2072,
    "name": "England",
    "code": "ENG",
    "flag": "https://crests.football-data.org/770.svg"
  },
  "currentSeason": {
    "id": 2345,
    "startDate": "2025-08-15",
    "endDate": "2026-05-24",
    "currentMatchday": 14
  }
}
```

### 2. 区域/国家 (Areas) ✅

**数量**: 272 个国家/地区

**数据结构**:
```json
{
  "id": 2072,
  "name": "England",
  "countryCode": "ENG",
  "flag": "https://crests.football-data.org/770.svg",
  "parentAreaId": 2077,
  "parentArea": "Europe"
}
```

### 3. 球队 (Teams) ✅

**示例**: 英超 20 支球队

**可用字段**:
- `id`: 球队ID
- `name`: 球队全称 (Arsenal FC)
- `shortName`: 简称 (Arsenal)
- `tla`: 三字缩写 (ARS)
- `crest`: 队徽URL
- `address`: 地址
- `website`: 官网
- `founded`: 成立年份
- `clubColors`: 球队颜色
- `venue`: 主场场馆
- `area`: 所属国家/地区
- `coach`: 教练信息
- `squad`: 球员阵容 (包含41名球员)
- `runningCompetitions`: 参加的竞赛
- `lastUpdated`: 最后更新时间

**教练数据结构**:
```json
{
  "id": 12345,
  "firstName": "Arne",
  "lastName": "Slot",
  "name": "Arne Slot",
  "nationality": "Netherlands",
  "contract": {
    "start": "2024-06-01",
    "until": "2027-06-30"
  }
}
```

**球员数据结构**:
```json
{
  "id": 67890,
  "name": "Alisson",
  "firstName": "Alisson",
  "lastName": "Becker",
  "dateOfBirth": "1992-10-02",
  "nationality": "Brazil",
  "position": "Goalkeeper",
  "shirtNumber": 1,
  "lastUpdated": "2024-01-15T10:30:00Z"
}
```

### 4. 比赛 (Matches) ✅

**今日比赛**: 33 场

**数据结构**:
```json
{
  "id": 554873,
  "utcDate": "2026-05-03T00:00:00Z",
  "status": "FINISHED",
  "matchday": 14,
  "stage": "REGULAR_SEASON",
  "homeTeam": {
    "id": 57,
    "name": "Arsenal FC",
    "shortName": "Arsenal",
    "tla": "ARS",
    "crest": "https://..."
  },
  "awayTeam": {...},
  "score": {
    "winner": "HOME_TEAM",
    "fullTime": {
      "home": 2,
      "away": 1
    },
    "halfTime": {
      "home": 1,
      "away": 0
    }
  },
  "odds": {...},
  "referees": [...]
}
```

## 数据存储位置

所有原始数据已保存到 `output/` 目录：

- `competitions.json` - 13个竞赛的完整数据
- `areas.json` - 272个国家/地区数据
- `teams_PL.json` - 英超20支球队的完整数据（含球员）
- `team_detail_64.json` - 利物浦球队详细信息
- `matches.json` - 今日比赛数据
- `summary_report.json` - 数据摘要报告

## 可以建立的标准化数据表

基于API返回的数据，我们可以建立以下标准表：

### 1. countries (国家表)
```sql
CREATE TABLE countries (
    id INTEGER PRIMARY KEY,          -- area.id
    name VARCHAR(100),               -- 国家名称
    code VARCHAR(10),                -- 国家代码 (ENG, ESP等)
    flag_url TEXT,                   -- 国旗URL
    parent_area_id INTEGER,          -- 父区域ID
    parent_area_name VARCHAR(100)    -- 父区域名称 (Europe, Asia等)
);
```

### 2. leagues (联赛表)
```sql
CREATE TABLE leagues (
    id INTEGER PRIMARY KEY,          -- competition.id
    name VARCHAR(100),               -- 联赛名称
    code VARCHAR(10),                -- 联赛代码 (PL, SA等)
    type VARCHAR(50),                -- 类型 (LEAGUE, CUP等)
    emblem_url TEXT,                 -- 联赛徽章URL
    country_id INTEGER,              -- 所属国家ID
    current_season_start DATE,       -- 当前赛季开始日期
    current_season_end DATE,         -- 当前赛季结束日期
    current_matchday INTEGER         -- 当前轮次
);
```

### 3. teams (球队表)
```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,          -- team.id
    name VARCHAR(100),               -- 球队全称
    short_name VARCHAR(50),          -- 简称
    tla VARCHAR(10),                 -- 三字缩写
    crest_url TEXT,                  -- 队徽URL
    founded INTEGER,                 -- 成立年份
    venue VARCHAR(100),              -- 主场
    website TEXT,                    -- 官网
    club_colors VARCHAR(50),         -- 球队颜色
    address TEXT,                    -- 地址
    country_id INTEGER,              -- 所属国家ID
    last_updated TIMESTAMP           -- 最后更新时间
);
```

### 4. coaches (教练表)
```sql
CREATE TABLE coaches (
    id INTEGER PRIMARY KEY,          -- coach.id
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    name VARCHAR(100),               -- 全名
    nationality VARCHAR(50),         -- 国籍
    contract_start DATE,             -- 合同开始
    contract_until DATE,             -- 合同结束
    team_id INTEGER                  -- 所属球队ID
);
```

### 5. players (球员表)
```sql
CREATE TABLE players (
    id INTEGER PRIMARY KEY,          -- player.id
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    name VARCHAR(100),               -- 全名
    date_of_birth DATE,              -- 出生日期
    nationality VARCHAR(50),         -- 国籍
    position VARCHAR(50),            -- 位置
    shirt_number INTEGER,            -- 球衣号码
    team_id INTEGER,                 -- 所属球队ID
    last_updated TIMESTAMP
);
```

### 6. matches (比赛表)
```sql
CREATE TABLE matches (
    id INTEGER PRIMARY KEY,          -- match.id
    utc_date TIMESTAMP,              -- 比赛时间
    status VARCHAR(20),              -- 状态
    matchday INTEGER,                -- 轮次
    stage VARCHAR(50),               -- 阶段
    league_id INTEGER,               -- 联赛ID
    home_team_id INTEGER,            -- 主队ID
    away_team_id INTEGER,            -- 客队ID
    home_score INTEGER,              -- 主队得分
    away_score INTEGER,              -- 客队得分
    half_time_home_score INTEGER,    -- 半场主队得分
    half_time_away_score INTEGER,    -- 半场客队得分
    winner VARCHAR(20),              -- 胜者
    venue VARCHAR(100)               -- 比赛场地
);
```

## 下一步计划

1. ✅ 完成API数据探索
2. ⏳ 设计数据库表结构
3. ⏳ 创建数据同步脚本
4. ⏳ 实现增量更新机制
5. ⏳ 考虑与现有项目的对接方案

## 注意事项

- **速率限制**: 免费账户约10次/分钟，需要合理控制请求频率
- **数据范围**: 仅包含13个主要联赛，不包括中国联赛
- **球员数据**: 部分球员的shirtNumber为None，可能需要处理
- **独立性**: 此项目完全独立，不与现有zqgetdata项目共享数据

## 测试记录

- 测试时间: 2026-05-03 23:36
- API响应: 正常
- 数据完整性: 良好
- 速率限制: 符合预期
