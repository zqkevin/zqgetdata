# 标准足球数据库 - 数据库设计方案

## 📊 数据源对比分析

### 1. football-data.org

**优势**:
- ✅ 数据结构清晰规范
- ✅ 提供完整的中英文双语支持（通过翻译）
- ✅ 包含国家、联赛、球队、球员层次结构
- ✅ 有区域层级关系（parent_area_id）
- ✅ 字段命名规范统一

**数据结构**:
```json
// countries.json
{
  "id": 2011,
  "name_en": "Argentina",
  "name_zh": "阿根廷",
  "code": "ARG",
  "flag": "url",
  "parent_area_id": 2220,
  "parent_area_name_en": "South America",
  "parent_area_name_zh": "南美洲"
}

// leagues.json
{
  "id": 2021,
  "name_en_full": "Premier League",
  "name_zh_full": "英格兰超级联赛",
  "name_zh_short": null,
  "code": "PL",
  "type": "LEAGUE",
  "emblem": "url",
  "area_id": 2072,
  "area_name_en": "England",
  "area_name_zh": "英格兰",
  "current_season": {
    "start_date": "2025-08-15",
    "end_date": "2026-05-24",
    "current_matchday": 35
  }
}

// teams_with_players.json
{
  "id": 57,
  "name_en_full": "Arsenal FC",
  "name_en_short": "Arsenal",
  "name_zh_full": "阿森纳",
  "name_zh_short": "阿森纳",
  "short_code": "ARS",
  "tla": "ARS",
  "crest": "url",
  "address": "...",
  "website": "url",
  "founded": 1886,
  "club_colors": "Red / White",
  "venue": "Emirates Stadium",
  "area_id": 2072,
  "area_name_en": "England",
  "area_name_zh": "英格兰",
  "coach": {
    "id": 123,
    "name_en": "Mikel Arteta",
    "name_zh": "米克尔·阿尔特塔",
    "nationality": "Spain"
  },
  "players": [
    {
      "id": 1230,
      "name_en": "Fábio",
      "name_en_full": "Fábio",
      "first_name_en": null,
      "last_name_en": null,
      "name_zh_full": "法比奥",
      "first_name_zh": null,
      "last_name_zh": null,
      "date_of_birth": "1990-01-01",
      "nationality": "Brazil",
      "position": "Goalkeeper",
      "shirt_number": 1
    }
  ]
}
```

---

### 2. API-Football

**优势**:
- ✅ 覆盖亚洲联赛（日本、韩国、中国、沙特等）
- ✅ 提供多个赛季历史数据
- ✅ 包含国家代码和国旗
- ✅ 数据结构简洁

**数据结构**:
```json
{
  "id": 39,
  "name": "Premier League",
  "type": "League",
  "logo": "url",
  "country": "England",
  "country_code": "GB-ENG",
  "country_flag": "url",
  "seasons": [
    {
      "year": 2025,
      "start": "2025-08-15",
      "end": "2026-05-24",
      "current": true
    }
  ]
}
```

**劣势**:
- ❌ 无中文支持
- ❌ 需要额外翻译
- ❌ 缺少详细的球队和球员信息

---

### 3. TheSportsDB

**优势**:
- ✅ **最详细和最丰富的数据** ⭐⭐⭐⭐⭐
- ✅ 多语言描述（EN, DE, FR, IT, JP, RU, ES, PT, NO等）
- ✅ 完整的球队信息（成立时间、球场容量、社交媒体等）
- ✅ 多个备用名称（strTeamAlternate）
- ✅ 颜色代码（strColour1, strColour2, strColour3）
- ✅ 丰富的媒体资源（徽章、Logo、球迷艺术图、横幅等）
- ✅ 跨平台ID映射（idAPIfootball, idESPN）
- ✅ 多联赛关联（strLeague, strLeague2, strLeague3...）

**数据结构**:
```json
{
  "idTeam": "133604",
  "idAPIfootball": "42",
  "strTeam": "Arsenal",
  "strTeamAlternate": "Arsenal Football Club, AFC, Arsenal FC",
  "strTeamShort": "ARS",
  "intFormedYear": "1892",
  "strSport": "Soccer",
  "strLeague": "English Premier League",
  "idLeague": "4328",
  "strLeague2": "FA Cup",
  "idLeague2": "4482",
  "strLeague3": "EFL Cup",
  "idLeague3": "4570",
  "strLeague4": "UEFA Champions League",
  "idLeague4": "4480",
  "idVenue": "15528",
  "strStadium": "Emirates Stadium",
  "intStadiumCapacity": "60338",
  "strLocation": "Holloway, London, England",
  "strWebsite": "www.arsenal.com",
  "strFacebook": "www.facebook.com/Arsenal",
  "strTwitter": "twitter.com/arsenal",
  "strInstagram": "instagram.com/arsenal",
  "strDescriptionEN": "...",
  "strDescriptionDE": "...",
  "strDescriptionFR": "...",
  "strDescriptionCN": null,
  "strColour1": "#EF0107",
  "strColour2": "#fbffff",
  "strColour3": "#013373",
  "strCountry": "England",
  "strBadge": "url",
  "strLogo": "url",
  "strFanart1": "url",
  "strFanart2": "url",
  "strBanner": "url",
  "strEquipment": "url",
  "strYoutube": "url"
}
```

**劣势**:
- ❌ 中文字段为null（strDescriptionCN）
- ❌ 需要翻译
- ❌ 数据结构较复杂，嵌套深

---

## 🎯 主数据源选择

### 推荐：**TheSportsDB 作为主数据源** ⭐⭐⭐⭐⭐

**理由**:
1. **数据最丰富**: 包含其他两个平台没有的详细信息
2. **多语言支持**: 已有多种语言描述，只需补充中文
3. **跨平台映射**: 包含API-Football ID，便于数据整合
4. **媒体资源**: 提供完整的图片资源链接
5. **社交信息**: 包含网站、社交媒体账号
6. **历史信息**: 成立年份、球场信息等

### 辅助数据源

- **football-data.org**: 用于补充欧洲主流联赛的结构化数据
- **API-Football**: 用于补充亚洲联赛数据

---

## 🗄️ 数据库表设计

基于JSON结构和外键索引原则，设计以下表结构：

### 1. areas (国家/地区表)

```sql
CREATE TABLE areas (
    id INT PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL,
    name_zh VARCHAR(100),
    code VARCHAR(10),
    flag_url TEXT,
    parent_area_id INT,
    area_type ENUM('WORLD', 'CONTINENT', 'COUNTRY', 'REGION') DEFAULT 'COUNTRY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_area_id) REFERENCES areas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_areas_parent ON areas(parent_area_id);
CREATE INDEX idx_areas_code ON areas(code);
```

**说明**:
- 存储世界、大洲、国家、地区层级关系
- 使用自引用外键实现树形结构
- 示例数据：World → Europe → England

---

### 2. leagues (联赛表)

```sql
CREATE TABLE leagues (
    id INT PRIMARY KEY,
    name_en_full VARCHAR(200) NOT NULL,
    name_en_short VARCHAR(100),
    name_zh_full VARCHAR(200),
    name_zh_short VARCHAR(100),
    code VARCHAR(20),
    type ENUM('LEAGUE', 'CUP', 'SUPER_CUP', 'OTHER') DEFAULT 'LEAGUE',
    emblem_url TEXT,
    logo_url TEXT,
    area_id INT NOT NULL,
    current_season_start DATE,
    current_season_end DATE,
    current_matchday INT,
    source_platform ENUM('FOOTBALL_DATA', 'API_FOOTBALL', 'THESPORTSDB') DEFAULT 'THESPORTSDB',
    source_id VARCHAR(50),  -- 原始平台的ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_leagues_area ON leagues(area_id);
CREATE INDEX idx_leagues_code ON leagues(code);
CREATE INDEX idx_leagues_source ON leagues(source_platform, source_id);
```

**说明**:
- 通过 area_id 外键关联到国家/地区
- 存储多个平台的ID以便数据整合
- 区分联赛类型（联赛、杯赛等）

---

### 3. venues (球场表)

```sql
CREATE TABLE venues (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    name_zh VARCHAR(200),
    city VARCHAR(100),
    country VARCHAR(100),
    address TEXT,
    capacity INT,
    surface VARCHAR(50),  -- 草皮类型
    image_url TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_venues_city ON venues(city);
CREATE INDEX idx_venues_country ON venues(country);
```

**说明**:
- 独立的球场表，避免数据冗余
- 多个球队可能共用同一个球场

---

### 4. teams (球队表)

```sql
CREATE TABLE teams (
    id INT PRIMARY KEY,
    name_en_full VARCHAR(200) NOT NULL,
    name_en_short VARCHAR(100),
    name_zh_full VARCHAR(200),
    name_zh_short VARCHAR(100),
    short_code VARCHAR(10),
    tla VARCHAR(10),  -- Three Letter Abbreviation
    founded_year INT,
    club_colors VARCHAR(100),
    website VARCHAR(500),
    
    -- 社交媒体
    facebook_url VARCHAR(500),
    twitter_url VARCHAR(500),
    instagram_url VARCHAR(500),
    youtube_url VARCHAR(500),
    
    -- 媒体资源
    crest_url TEXT,
    badge_url TEXT,
    logo_url TEXT,
    banner_url TEXT,
    equipment_url TEXT,
    fanart1_url TEXT,
    fanart2_url TEXT,
    fanart3_url TEXT,
    fanart4_url TEXT,
    
    -- 关联外键
    area_id INT,  -- 所属国家/地区
    venue_id INT,  -- 主场球场
    
    -- 跨平台ID映射
    api_football_id VARCHAR(50),
    espn_id VARCHAR(50),
    thesportsdb_id VARCHAR(50),
    
    -- 来源信息
    source_platform ENUM('FOOTBALL_DATA', 'API_FOOTBALL', 'THESPORTSDB') DEFAULT 'THESPORTSDB',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id),
    FOREIGN KEY (venue_id) REFERENCES venues(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_teams_area ON teams(area_id);
CREATE INDEX idx_teams_venue ON teams(venue_id);
CREATE INDEX idx_teams_api_football ON teams(api_football_id);
CREATE INDEX idx_teams_thesportsdb ON teams(thesportsdb_id);
CREATE INDEX idx_teams_name_en ON teams(name_en_full);
CREATE INDEX idx_teams_name_zh ON teams(name_zh_full);
```

**说明**:
- 核心球队信息表
- 包含所有平台的ID映射，方便数据整合
- 丰富的媒体资源字段

---

### 5. team_leagues (球队-联赛关联表)

```sql
CREATE TABLE team_leagues (
    id INT PRIMARY KEY AUTO_INCREMENT,
    team_id INT NOT NULL,
    league_id INT NOT NULL,
    season_year INT,
    is_primary BOOLEAN DEFAULT FALSE,  -- 是否为主要联赛
    joined_date DATE,
    left_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE,
    UNIQUE KEY uk_team_league_season (team_id, league_id, season_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_team_leagues_team ON team_leagues(team_id);
CREATE INDEX idx_team_leagues_league ON team_leagues(league_id);
```

**说明**:
- 多对多关系：一个球队可以参加多个联赛
- 记录历史参赛信息
- 标记主要联赛（is_primary）

---

### 6. positions (位置表)

```sql
CREATE TABLE positions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL UNIQUE,  -- GK, DF, MF, FW
    name_en VARCHAR(50) NOT NULL,
    name_zh VARCHAR(50),
    category ENUM('GOALKEEPER', 'DEFENDER', 'MIDFIELDER', 'FORWARD') NOT NULL,
    sort_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 预置数据
INSERT INTO positions (code, name_en, name_zh, category, sort_order) VALUES
('GK', 'Goalkeeper', '守门员', 'GOALKEEPER', 1),
('CB', 'Centre-Back', '中后卫', 'DEFENDER', 2),
('LB', 'Left-Back', '左后卫', 'DEFENDER', 3),
('RB', 'Right-Back', '右后卫', 'DEFENDER', 4),
('CDM', 'Defensive Midfield', '防守型中场', 'MIDFIELDER', 5),
('CM', 'Central Midfield', '中场', 'MIDFIELDER', 6),
('CAM', 'Attacking Midfield', '攻击型中场', 'MIDFIELDER', 7),
('LM', 'Left Midfield', '左中场', 'MIDFIELDER', 8),
('RM', 'Right Midfield', '右中场', 'MIDFIELDER', 9),
('LW', 'Left Winger', '左边锋', 'FORWARD', 10),
('RW', 'Right Winger', '右边锋', 'FORWARD', 11),
('CF', 'Centre-Forward', '中锋', 'FORWARD', 12),
('ST', 'Striker', '前锋', 'FORWARD', 13);
```

**说明**:
- 标准化的位置字典表
- 避免在球员表中重复存储位置名称

---

### 7. players (球员表)

```sql
CREATE TABLE players (
    id INT PRIMARY KEY,
    name_en_full VARCHAR(200) NOT NULL,
    first_name_en VARCHAR(100),
    last_name_en VARCHAR(100),
    name_zh_full VARCHAR(200),
    first_name_zh VARCHAR(100),
    last_name_zh VARCHAR(100),
    
    date_of_birth DATE,
    age INT GENERATED ALWAYS AS (TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE())) STORED,
    nationality VARCHAR(100),
    nationality_area_id INT,  -- 关联到areas表
    
    position_id INT,  -- 关联到positions表
    position_detail VARCHAR(50),  -- 详细位置（如"Centre-Back"）
    
    height_cm INT,
    weight_kg INT,
    preferred_foot ENUM('LEFT', 'RIGHT', 'BOTH'),
    
    shirt_number INT,
    
    -- 媒体资源
    photo_url TEXT,
    
    -- 跨平台ID
    api_football_id VARCHAR(50),
    thesportsdb_id VARCHAR(50),
    
    -- 来源信息
    source_platform ENUM('FOOTBALL_DATA', 'API_FOOTBALL', 'THESPORTSDB') DEFAULT 'THESPORTSDB',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (nationality_area_id) REFERENCES areas(id),
    FOREIGN KEY (position_id) REFERENCES positions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_players_nationality ON players(nationality_area_id);
CREATE INDEX idx_players_position ON players(position_id);
CREATE INDEX idx_players_dob ON players(date_of_birth);
CREATE INDEX idx_players_name_en ON players(name_en_full);
CREATE INDEX idx_players_name_zh ON players(name_zh_full);
```

**说明**:
- 计算字段 `age` 自动根据出生日期计算
- 国籍关联到 areas 表实现标准化
- 位置关联到 positions 字典表

---

### 8. player_teams (球员-球队关联表)

```sql
CREATE TABLE player_teams (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT NOT NULL,
    team_id INT NOT NULL,
    shirt_number INT,
    join_date DATE,
    leave_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    contract_until DATE,
    market_value_eur INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    UNIQUE KEY uk_player_team_current (player_id, team_id, is_current)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_player_teams_player ON player_teams(player_id);
CREATE INDEX idx_player_teams_team ON player_teams(team_id);
CREATE INDEX idx_player_teams_current ON player_teams(is_current);
```

**说明**:
- 记录球员转会历史
- 支持一个球员在不同时期效力不同球队
- is_current 标记当前效力的球队

---

### 9. coaches (教练表)

```sql
CREATE TABLE coaches (
    id INT PRIMARY KEY,
    name_en VARCHAR(200) NOT NULL,
    name_zh VARCHAR(200),
    date_of_birth DATE,
    nationality VARCHAR(100),
    nationality_area_id INT,
    photo_url TEXT,
    
    -- 跨平台ID
    api_football_id VARCHAR(50),
    thesportsdb_id VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (nationality_area_id) REFERENCES areas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_coaches_nationality ON coaches(nationality_area_id);
CREATE INDEX idx_coaches_name_en ON coaches(name_en);
CREATE INDEX idx_coaches_name_zh ON coaches(name_zh);
```

---

### 10. team_coaches (球队-教练关联表)

```sql
CREATE TABLE team_coaches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    team_id INT NOT NULL,
    coach_id INT NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'HEAD_COACH',  -- HEAD_COACH, ASSISTANT, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (coach_id) REFERENCES coaches(id) ON DELETE CASCADE,
    UNIQUE KEY uk_team_coach_current (team_id, coach_id, is_current)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 索引
CREATE INDEX idx_team_coaches_team ON team_coaches(team_id);
CREATE INDEX idx_team_coaches_coach ON team_coaches(coach_id);
CREATE INDEX idx_team_coaches_current ON team_coaches(is_current);
```

---

### 11. translations (翻译缓存表)

```sql
CREATE TABLE translations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    source_text VARCHAR(500) NOT NULL,
    translated_text VARCHAR(500) NOT NULL,
    from_lang CHAR(2) DEFAULT 'en',
    to_lang CHAR(2) DEFAULT 'zh',
    context VARCHAR(50),  -- COUNTRY, LEAGUE, TEAM, PLAYER, etc.
    md5_hash CHAR(32) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_md5 (md5_hash),
    INDEX idx_context (context)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**说明**:
- 替代JSON缓存文件
- 使用MD5哈希快速查找
- 支持多种语言对

---

## 📈 ER图关系

```
areas (国家/地区)
  ├── leagues (联赛) [area_id]
  ├── teams (球队) [area_id]
  ├── players (球员) [nationality_area_id]
  └── coaches (教练) [nationality_area_id]

venues (球场)
  └── teams (球队) [venue_id]

leagues (联赛)
  └── team_leagues (球队-联赛关联) [league_id]

teams (球队)
  ├── team_leagues (球队-联赛关联) [team_id]
  ├── player_teams (球员-球队关联) [team_id]
  └── team_coaches (球队-教练关联) [team_id]

positions (位置字典)
  └── players (球员) [position_id]

players (球员)
  └── player_teams (球员-球队关联) [player_id]

coaches (教练)
  └── team_coaches (球队-教练关联) [coach_id]
```

---

## 🎯 设计原则

### 1. 外键索引化
- 所有关联字段都建立外键约束
- 频繁查询的字段添加索引
- 使用级联删除保持数据一致性

### 2. 数据规范化
- 避免数据冗余（如国家、位置使用字典表）
- 多对多关系使用中间表
- 分离静态数据和动态数据

### 3. 跨平台兼容
- 每个实体保存各平台的原始ID
- 使用 source_platform 标记数据来源
- 便于数据整合和去重

### 4. 多语言支持
- 所有名称字段都有英文和中文版本
- 翻译缓存独立存储
- 易于扩展其他语言

### 5. 可扩展性
- 预留扩展字段
- 使用ENUM限制取值范围
- 时间戳追踪数据变更

---

## 🚀 下一步实施计划

1. **创建数据库迁移脚本**
   - 编写SQL建表脚本
   - 添加初始数据（positions字典）
   
2. **数据导入工具**
   - 从JSON文件导入基础数据
   - 处理跨平台ID映射
   - 执行翻译任务
   
3. **数据验证**
   - 检查外键完整性
   - 验证数据一致性
   - 抽样检查翻译质量

4. **API接口开发**
   - 基于新表结构开发REST API
   - 支持中英文双语查询
   - 提供数据过滤和分页

---

**文档版本**: 1.0  
**创建日期**: 2026-05-07  
**作者**: AI Assistant
