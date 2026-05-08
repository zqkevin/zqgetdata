# 多语言支持说明

## 概述

本项目实现了完整的多语言支持，所有数据都包含英文和中文名称字段。

## 数据结构

### 1. 国家/地区 (countries.json)

```json
{
  "id": 2072,
  "name_en": "England",           // 英文名称
  "name_zh": "英格兰",             // 中文名称
  "code": "ENG",                   // 国家代码
  "flag": "https://...",           // 国旗URL
  "parent_area_id": 2077,
  "parent_area_name_en": "Europe", // 父区域英文名
  "parent_area_name_zh": "欧洲"     // 父区域中文名
}
```

**字段说明**:
- `name_en`: 英文名称（API原始数据）
- `name_zh`: 中文名称（通过映射表翻译）
- `parent_area_name_en/zh`: 父区域的中英文名称

### 2. 联赛 (leagues.json)

```json
{
  "id": 2021,
  "name_en": "Premier League",     // 英文名称
  "name_en_full": "Premier League", // 英文全称
  "name_zh": "英超",                // 中文简称
  "name_zh_full": "英格兰超级联赛",  // 中文全称
  "name_zh_short": null,            // 中文简称（备用）
  "code": "PL",
  "type": "LEAGUE",
  "emblem": "https://...",
  "area_id": 2072,
  "area_name_en": "England",       // 所属国家英文
  "area_name_zh": "英格兰",         // 所属国家中文
  "area_code": "ENG",
  "current_season": {...}
}
```

**字段说明**:
- `name_en/name_en_full`: 英文名称和全称
- `name_zh`: 中文简称（常用名）
- `name_zh_full`: 中文全称（正式名）
- `name_zh_short`: 中文简称（备用字段）
- `area_name_en/zh`: 所属国家的中英文名称

### 3. 球队 (teams_with_players.json)

```json
{
  "id": 57,
  "name_en": "Arsenal FC",         // 英文全称
  "name_en_full": "Arsenal FC",    // 英文全称
  "name_en_short": "Arsenal",      // 英文简称
  "tla": "ARS",                    // 三字缩写
  "name_zh": "阿森纳",              // 中文简称
  "name_zh_full": "阿森纳足球俱乐部", // 中文全称
  "name_zh_short": null,            // 中文简称（备用）
  "crest": "https://...",
  "founded": 1886,
  "venue": "Emirates Stadium",
  "website": "http://www.arsenal.com",
  "club_colors": "Red / White",
  "address": "...",
  "area_id": 2072,
  "area_name_en": "England",       // 所属国家英文
  "area_name_zh": "英格兰",         // 所属国家中文
  "league_code": "PL",
  "coach": {
    "id": 12345,
    "name_en": "Mikel Arteta",     // 教练英文名
    "name_zh": null,                // 教练中文名（待翻译）
    "nationality": "Spain",
    "contract_start": "2019-12-20",
    "contract_until": "2025-06-30"
  },
  "players": [
    {
      "id": 67890,
      "name_en": "Bukayo Saka",    // 球员英文名
      "name_en_full": "Bukayo Saka",
      "first_name_en": "Bukayo",
      "last_name_en": "Saka",
      "name_zh": null,              // 球员中文名（待翻译）
      "name_zh_full": null,
      "first_name_zh": null,
      "last_name_zh": null,
      "date_of_birth": "2001-09-05",
      "nationality": "England",
      "position": "Midfield",
      "shirt_number": 7
    }
  ]
}
```

**字段说明**:
- **球队名称**:
  - `name_en/name_en_full`: 英文全称
  - `name_en_short`: 英文简称
  - `tla`: 三字缩写（国际通用）
  - `name_zh/name_zh_full`: 中文简称和全称
  
- **教练名称**:
  - `name_en`: 英文姓名
  - `name_zh`: 中文姓名（待翻译）
  
- **球员名称**:
  - `name_en/name_en_full`: 英文全名
  - `first_name_en/last_name_en`: 英文名和姓
  - `name_zh/name_zh_full`: 中文全名（待翻译）
  - `first_name_zh/last_name_zh`: 中文名和姓（待翻译）

## 翻译状态

### 已完成翻译

✅ **国家/地区**: 11/272 (主要国家已翻译)
- England → 英格兰
- Spain → 西班牙
- Germany → 德国
- Italy → 意大利
- France → 法国
- Brazil → 巴西
- Netherlands → 荷兰
- Portugal → 葡萄牙
- Europe → 欧洲
- South America → 南美洲
- World → 世界

✅ **联赛**: 13/13 (全部已翻译)
- Premier League → 英超 / 英格兰超级联赛
- Championship → 英冠 / 英格兰冠军联赛
- Primera Division → 西甲 / 西班牙甲级联赛
- Bundesliga → 德甲 / 德国甲级联赛
- Serie A → 意甲 / 意大利甲级联赛
- Ligue 1 → 法甲 / 法国甲级联赛
- Eredivisie → 荷甲 / 荷兰甲级联赛
- Primeira Liga → 葡超 / 葡萄牙超级联赛
- Campeonato Brasileiro Série A → 巴甲 / 巴西甲级联赛
- UEFA Champions League → 欧冠 / 欧洲冠军联赛
- European Championship → 欧洲杯 / 欧洲足球锦标赛
- Copa Libertadores → 解放者杯 / 南美解放者杯
- FIFA World Cup → 世界杯 / 国际足联世界杯

✅ **球队**: 10/331 (示例球队已翻译)
- Arsenal FC → 阿森纳 / 阿森纳足球俱乐部
- Liverpool FC → 利物浦 / 利物浦足球俱乐部
- Manchester United FC → 曼联 / 曼彻斯特联足球俱乐部
- Manchester City FC → 曼城 / 曼彻斯特城足球俱乐部
- Chelsea FC → 切尔西 / 切尔西足球俱乐部

### 待翻译

⏳ **国家/地区**: 261个（次要国家和地区）
⏳ **球队**: 321支
⏳ **教练**: 331名
⏳ **球员**: 9,757名

## 如何添加翻译

### 方法1: 编辑映射表（推荐）

编辑 `translate_names.py` 文件中的映射表：

```python
# 添加国家翻译
COUNTRY_ZH_MAP = {
    "Argentina": "阿根廷",
    "Japan": "日本",
    # ...
}

# 添加联赛翻译
LEAGUE_ZH_MAP = {
    "New League": {
        "full": "新联赛全称",
        "short": "新联赛简称"
    },
    # ...
}

# 添加球队翻译
TEAM_ZH_MAP = {
    "Team Name FC": {
        "full": "球队中文全称",
        "short": "球队中文简称"
    },
    # ...
}
```

然后运行：
```bash
python translate_names.py
```

### 方法2: 直接编辑JSON文件

直接编辑 `data/` 目录下的JSON文件，填充 `*_zh` 字段。

### 方法3: 使用翻译API（未来扩展）

可以集成翻译API自动翻译，但需要人工校对以确保准确性。

## 使用示例

### Python示例

```python
import json

# 加载数据
with open('data/leagues.json', encoding='utf-8') as f:
    leagues = json.load(f)

# 获取英超的中文名称
pl = next(l for l in leagues if l['code'] == 'PL')
print(f"英文: {pl['name_en']}")          # Premier League
print(f"中文简称: {pl['name_zh']}")       # 英超
print(f"中文全称: {pl['name_zh_full']}")  # 英格兰超级联赛

# 加载球队数据
with open('data/teams_with_players.json', encoding='utf-8') as f:
    teams = json.load(f)

# 获取阿森纳的中英文名称
arsenal = next(t for t in teams if t['tla'] == 'ARS')
print(f"英文全称: {arsenal['name_en_full']}")     # Arsenal FC
print(f"英文简称: {arsenal['name_en_short']}")    # Arsenal
print(f"中文全称: {arsenal['name_zh_full']}")     # 阿森纳足球俱乐部
print(f"中文简称: {arsenal['name_zh']}")          # 阿森纳
```

### SQL查询示例

如果导入数据库后：

```sql
-- 查询球队的多种语言名称
SELECT 
    id,
    name_en AS english_name,
    name_en_short AS english_short,
    name_zh AS chinese_name,
    name_zh_full AS chinese_full,
    tla AS abbreviation
FROM teams
WHERE league_code = 'PL';

-- 根据中文名称搜索球队
SELECT * FROM teams 
WHERE name_zh LIKE '%阿森纳%' 
   OR name_zh_full LIKE '%阿森纳%';

-- 多语言联赛信息
SELECT 
    code,
    name_en AS league_name_en,
    name_zh AS league_name_zh,
    name_zh_full AS league_name_zh_full,
    area_name_en AS country_en,
    area_name_zh AS country_zh
FROM leagues;
```

## 最佳实践

### 1. 命名规范

- **英文**: 使用API提供的原始名称
- **中文简称**: 常用的简短名称（如"英超"、"阿森纳"）
- **中文全称**: 正式的完整名称（如"英格兰超级联赛"、"阿森纳足球俱乐部"）

### 2. 翻译优先级

1. **高优先级**: 主流联赛和知名球队
2. **中优先级**: 次级联赛和一般球队
3. **低优先级**: 冷门联赛和小球队

### 3. 质量控制

- ✅ 使用官方中文名称（如有）
- ✅ 参考权威媒体译名
- ✅ 保持一致性（同一球队译名统一）
- ⚠️ 避免直译导致的歧义
- ⚠️ 注意音译和意译的选择

### 4. 更新策略

- 定期同步API数据（`sync_data.py`）
- 同步后运行翻译脚本（`translate_names.py`）
- 手动补充新增数据的翻译
- 版本控制映射表的变更

## 未来扩展

### 可能的改进

1. **更多语言支持**
   - 添加西班牙语 (name_es)
   - 添加法语 (name_fr)
   - 添加德语 (name_de)

2. **自动翻译**
   - 集成Google Translate API
   - 集成百度翻译API
   - 人工校对机制

3. **社区贡献**
   - 允许用户提交翻译
   - 审核机制
   - 众包翻译平台

4. **智能匹配**
   - 基于拼音的模糊搜索
   - 别名和俗称支持
   - 历史名称记录

## 注意事项

⚠️ **重要提醒**:

1. **API限制**: football-data.org只提供英文数据，中文需要自行翻译
2. **准确性**: 翻译质量直接影响用户体验，建议仔细校对
3. **一致性**: 保持译名的统一性，避免同一实体多个译名
4. **维护成本**: 331支球队和9757名球员的翻译工作量较大
5. **动态更新**: 球员转会、教练更换等需要及时更新

## 总结

本项目通过以下字段实现多语言支持：

| 实体 | 英文字段 | 中文字段 | 说明 |
|------|---------|---------|------|
| 国家 | name_en | name_zh | 国家名称 |
| 联赛 | name_en, name_en_full | name_zh, name_zh_full | 联赛名称（含简称和全称） |
| 球队 | name_en, name_en_short | name_zh, name_zh_full | 球队名称（含简称和全称） |
| 教练 | name_en | name_zh | 教练姓名 |
| 球员 | name_en, first_name_en, last_name_en | name_zh, first_name_zh, last_name_zh | 球员姓名 |

这种设计既保留了原始的英文数据，又提供了本地化的中文名称，便于不同语言环境的使用。
