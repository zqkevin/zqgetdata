# Standard Football Database - 标准足球数据库

## 📁 项目结构

```
standard_football_db/
├── data/                          # 数据文件目录
│   ├── countries.json            # 国家/地区数据（272条，已翻译）
│   ├── leagues.json              # 联赛数据（17条，已规范化）
│   ├── teams_with_players.json   # 球队和球员数据（336支球队，9757名球员，已翻译）
│   └── summary.json              # 数据摘要
│
├── tools/                         # 工具脚本目录
│   ├── baidu_translate/          # 百度翻译相关工具
│   │   ├── baidu_translate.py    # 百度翻译API封装
│   │   └── translations_cache.json # 翻译缓存（10,000+条记录）
│   │
│   ├── football-data.org/        # football-data.org平台工具
│   │   ├── explore_api.py        # API探索工具
│   │   ├── extend_data.py        # 数据扩展工具
│   │   ├── sync_data.py          # 数据同步工具
│   │   └── translate_names.py    # 名称翻译工具
│   │
│   ├── api-football/             # API-Football平台工具（待添加）
│   │
│   ├── translate_all.py          # 统一翻译工具
│   ├── complete_player_data.py   # 完善球员数据（翻译+拆分名字）
│   ├── clean_leagues.py          # 清理联赛冗余字段
│   ├── fix_translation_errors.py # 修正国家翻译错误
│   ├── fix_team_translations.py  # 修正球队翻译错误
│   └── check_translation_quality.py # 翻译质量检查工具
│
├── docs/                          # 文档目录
│   ├── guides/                   # 使用指南
│   ├── WORK_SUMMARY_2026-05-03.md
│   ├── TRANSLATION_WORK_SUMMARY.md
│   ├── TRANSLATION_COMPLETION_REPORT.md
│   └── TRANSLATION_FINAL_REPORT.md
│
├── output/                        # 输出文件目录
├── README.md                      # 项目说明（本文件）
└── .gitignore                     # Git忽略配置
```

---

## 🎯 项目概述

这是一个标准化的足球数据库项目，整合了多个数据源的信息，提供完整的中英文双语数据。

### 数据来源

1. **football-data.org**: 主要数据源，提供欧洲主流联赛数据
2. **API-Football**: 补充亚洲联赛数据
3. **百度翻译API**: 提供中英文名称翻译

### 核心功能

- ✅ 多平台数据整合
- ✅ 中英文双语支持
- ✅ 智能翻译和缓存
- ✅ 名字自动拆分（first_name / last_name）
- ✅ 数据质量检查和修正

---

## 🚀 快速开始

### 1. 查看现有数据

```bash
cd standard_football_db
ls data/
```

### 2. 翻译新数据

```bash
# 使用统一翻译工具
python tools/translate_all.py

# 选择要翻译的数据文件：
# 1. countries.json
# 2. leagues.json  
# 3. teams_with_players.json
# 4. 全部翻译
```

### 3. 完善球员数据

```bash
# 翻译所有球员并自动拆分名字
python tools/complete_player_data.py
```

### 4. 检查翻译质量

```bash
python tools/check_translation_quality.py
```

### 5. 修正翻译错误

```bash
# 修正国家翻译
python tools/fix_translation_errors.py

# 修正球队翻译
python tools/fix_team_translations.py
```

---

## 📊 数据统计

### 当前数据量

| 数据类型 | 数量 | 翻译状态 |
|---------|------|---------|
| 国家/地区 | 272 | ✅ 100% |
| 联赛 | 17 | ✅ 100% |
| 球队 | 336 | ✅ 100% |
| 球员 | 9,757 | ✅ 100% |
| 教练 | ~336 | ✅ 100% |

### 翻译缓存

- **缓存文件**: `tools/baidu_translate/translations_cache.json`
- **缓存记录**: 10,000+条
- **命中率**: 第二次运行100%
- **速度提升**: 50倍+

---

## 🛠️ 工具说明

### 百度翻译工具 (`tools/baidu_translate/`)

**baidu_translate.py**
- 功能: 百度翻译API封装
- 特性: 
  - 自动签名生成
  - 批量翻译支持
  - QPS控制（1次/秒）
  - 缓存管理

**使用示例**:
```python
from tools.baidu_translate.baidu_translate import translate_text

# 翻译单个文本
result = translate_text('Manchester United', 'en', 'zh')
print(result)  # 输出: 曼彻斯特联
```

### football-data.org 工具 (`tools/football-data.org/`)

**explore_api.py**
- 功能: 探索和测试API端点
- 用途: 发现可用的数据和字段

**extend_data.py**
- 功能: 扩展现有数据
- 用途: 获取更多赛季、球队等信息

**sync_data.py**
- 功能: 同步最新数据
- 用途: 更新比赛结果、排名等动态数据

**translate_names.py**
- 功能: 翻译名称
- 用途: 将英文名称翻译为中文

### 通用工具 (`tools/`)

**translate_all.py**
- 功能: 统一翻译入口
- 支持: 所有JSON数据文件
- 特性: 交互式选择，带进度显示

**complete_player_data.py**
- 功能: 完善球员数据
- 操作:
  1. 翻译所有未翻译的球员
  2. 自动拆分英文名字到 first_name_en / last_name_en
  3. 自动拆分中文名字到 first_name_zh / last_name_zh

**clean_leagues.py**
- 功能: 清理联赛数据
- 操作: 删除冗余的 name_zh 字段

**fix_translation_errors.py**
- 功能: 修正国家翻译错误
- 示例: Turkey: 火鸡 → 土耳其

**fix_team_translations.py**
- 功能: 修正球队翻译错误
- 示例: NEC: 日本电气 → 奈梅亨

**check_translation_quality.py**
- 功能: 检查翻译质量
- 检测:
  - 缩写误译
  - 翻译过长
  - 未翻译项

---

## 📝 数据规范

### 字段命名规范

#### 国家/地区 (countries.json)
```json
{
  "id": 2011,
  "name_en": "Argentina",
  "name_zh": "阿根廷",
  "code": "ARG",
  "flag": "https://...",
  "parent_area_id": 2220,
  "parent_area_name_en": "South America",
  "parent_area_name_zh": "南美洲"
}
```

#### 联赛 (leagues.json)
```json
{
  "id": 2019,
  "name_en": "Serie A",
  "name_en_full": "Serie A",
  "name_zh_full": "意大利甲级联赛",
  "name_zh_short": null,
  "code": "SA",
  "area_name_en": "Italy",
  "area_name_zh": "意大利"
}
```

#### 球队 (teams_with_players.json)
```json
{
  "id": 1765,
  "name_en": "Fluminense FC",
  "name_en_full": "Fluminense FC",
  "name_en_short": "Fluminense",
  "name_zh_full": "弗卢米嫩塞",
  "name_zh_short": "弗卢米嫩塞",
  "area_name_en": "Brazil",
  "area_name_zh": "巴西"
}
```

#### 球员 (teams_with_players.json)
```json
{
  "id": 1230,
  "name_en": "Fábio",
  "name_en_full": "Fábio",
  "first_name_en": null,
  "last_name_en": null,
  "name_zh_full": "法比奥",
  "first_name_zh": null,
  "last_name_zh": null,
  "nationality": "Brazil",
  "position": "Goalkeeper"
}
```

### 名字拆分规则

**英文名**: 按空格拆分
- "Lucas Emanuel" → first_name="Lucas", last_name="Emanuel"
- "Juan Carlos Rodriguez" → first_name="Juan", last_name="Carlos Rodriguez"

**中文名**: 按分隔符拆分（·、空格、・）
- "卢卡斯·伊曼纽尔" → first_name="卢卡斯", last_name="伊曼纽尔"
- "吉列尔梅 阿兰纳" → first_name="吉列尔梅", last_name="阿兰纳"

---

## 🔧 开发指南

### 添加新平台支持

1. 在 `tools/` 下创建平台目录
   ```bash
   mkdir tools/new-platform
   ```

2. 添加平台特定的工具脚本

3. 在 `translate_all.py` 中添加支持

### 扩展翻译功能

1. 修改 `tools/baidu_translate/baidu_translate.py`
2. 更新缓存机制
3. 添加新的语言支持

### 数据验证

```bash
# 检查数据完整性
python tools/check_translation_quality.py

# 手动验证抽样数据
python -c "import json; data = json.load(open('data/teams_with_players.json')); print(f'总球队: {len(data)}')"
```

---

## 📈 性能优化

### 翻译缓存

- **位置**: `tools/baidu_translate/translations_cache.json`
- **格式**: JSON字典 `{原文: 译文}`
- **优势**: 避免重复翻译，提高速度50倍+

### 批量处理

- 使用 `complete_player_data.py` 批量翻译球员
- 每1.2秒一次请求（符合百度API QPS限制）
- 自动保存进度，支持断点续传

---

## ⚠️ 注意事项

### 1. 翻译质量

虽然百度翻译准确率很高（>97%），但仍可能出现错误：
- 缩写误译（如 NEC → 日本电气）
- 专有名词翻译不准确

**解决方案**:
- 使用修正工具批量修复
- 维护术语词典
- 定期检查和更新

### 2. API配额

百度翻译标准版：
- ✅ 完全免费
- ✅ 不限字符量
- ⚠️ QPS=1（每秒1次请求）

### 3. 数据备份

建议定期备份：
```bash
# 备份数据文件
cp data/*.json data/backup/

# 备份翻译缓存
cp tools/baidu_translate/translations_cache.json backups/
```

---

## 🤝 贡献指南

### 报告问题

如发现翻译错误或数据问题，请：
1. 检查是否是已知问题
2. 提交issue描述问题
3. 提供修正建议

### 改进翻译

1. 在 `tools/fix_team_translations.py` 中添加修正映射
2. 运行修正脚本
3. 提交PR

---

## 📞 联系方式

- GitHub: [zqkevin](https://github.com/zqkevin)
- 项目路径: `E:\my_prog\zqgetdata\standard_football_db`

---

## 📄 许可证

本项目仅供学习和研究使用。

---

**最后更新**: 2026-05-07  
**版本**: 1.0.0  
**状态**: ✅ 生产就绪
