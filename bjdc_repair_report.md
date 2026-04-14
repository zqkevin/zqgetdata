# 北京单场数据采集器修复报告

## 修复时间
2026-04-03

## 修复内容

### 1. 联赛处理逻辑优化 ✓

**问题分析：**
- 原有代码在联赛不存在时直接返回 None，导致比赛数据无法保存
- 不同数据源的联赛名称格式不统一（如"澳大利亚超级联赛"vs"澳超"）

**修复方案：**
1. 统一使用 `_utils.py` 中的 `handle_league_name()` 函数
2. 支持多种匹配方式：
   - 联赛全称匹配
   - 联赛简称匹配
   - 模糊匹配（包含关系）
   - 自动新增不存在的联赛
3. 与 tczq 采用相同的处理策略

**代码位置：**
- `app/crawler/bjdc.py` - `_process_league_and_match()` 方法
- `app/common/_utils.py` - `handle_league_name()` 函数

### 2. SPF 关系定义修复 ✓

**问题分析：**
- SQLAlchemy 无法自动确定 TczqMatch/BjdcMatch 与赔率表之间的外键关系
- 报错：`Could not determine join condition between parent/child tables`

**修复方案：**
1. 在 `TczqMatch`和`BjdcMatch` 模型中使用 `primaryjoin` 明确指定连接条件
2. 使用 `foreign()` 函数标识外键字段
3. 格式：`primaryjoin="and_(Match.match_id == foreign(Odds.match_id))"`

**修复文件：**
- `app/database/tczq_models.py` - TczqMatch 的所有赔率关系
- `app/database/bjdc_models.py` - BjdcMatch 的所有赔率关系

### 3. 赔率数据保存完善 ✓

**总进球赔率 (_get_zjq)：**
- 提取 0-6 球的赔率（HTML td 索引 6-12）
- 提取"其他"赔率（HTML td 索引 13）
- 检查是否已存在记录
- 不存在则新增，存在则更新

**比分赔率 (_get_bifen)：**
- 解析 HTML 中的比分表结构
- 提取所有比分组合的赔率（1:0, 2:0, 2:1 等）
- 提取"胜其他"、"负其他"、"平其他"赔率
- 动态映射到数据库字段
- 检查是否已存在记录
- 不存在则新增，存在则更新

**代码位置：**
- `app/crawler/bjdc.py` - `_get_zjq()` 和 `_get_bifen()` 方法

## 数据库验证结果

### 数据统计（2026-04-03 12:18）

| 表名 | 记录数 | 说明 |
|------|--------|------|
| bjdc_match | 97 | 北京单场比赛记录 |
| bjdc_total_goal_odds | 97 | 总进球赔率记录 |
| bjdc_score_odds | 97 | 比分赔率记录 |
| league | 1152 | 联赛记录（包含新增的） |
| team | 336 | 球队记录（包含新增的） |

### 示例数据

**比赛记录：**
```sql
match_id: 1337819
issue: "26042"
league_name: "澳大利亚超级联赛"
home_team: "阿德莱德联"
away_team: "奥克兰 FC"
```

**总进球赔率：**
```sql
match_id: 1337819
goal_0: 15.33
goal_1: 9.25
goal_2: 7.65
goal_3: 5.24
```

**比分赔率：**
```sql
match_id: 1337819
score_1_0: 31.78
score_2_0: 41.69
score_2_1: 15.52
```

## 测试流程

1. **创建采集器实例**
   ```python
   from app.crawler.bjdc import BjdcDataCollector
   collector = BjdcDataCollector()
   ```

2. **执行数据采集**
   ```python
   result = collector.get_gamedata()
   # 返回：True (成功)
   ```

3. **验证数据库记录**
   - 使用 MySQL 查询工具验证各表记录数
   - 抽样检查数据完整性
   - 验证关联关系正确性

## 技术要点

### 1. 联赛名称处理策略
```python
# 优先级顺序
1. 联赛全称精确匹配
2. 联赛简称精确匹配
3. 模糊匹配（长度>3 时）
   - 检查是否包含某个联赛的简称
   - 检查是否被某个联赛全称包含
4. 自动新增联赛记录
```

### 2. SQLAlchemy 关系定义
```python
# 使用 primaryjoin 明确连接条件
spf = relationship(
    'BjdcSpfOdds',
    primaryjoin="and_(BjdcMatch.match_id == foreign(BjdcSpfOdds.match_id))",
    backref='match',
    uselist=False,
    lazy=True
)
```

### 3. 赔率数据保存逻辑
```python
# 检查 - 新增/更新模式
existing = query(Odds).filter_by(match_id=fid).first()
if not existing:
    new_odds = Odds(match_id=fid, ...)
    localdb.add(new_odds, close=False)
else:
    # 更新现有记录
    for field, value in odds_dict.items():
        setattr(existing, field, value)
    localdb.update(existing, close=False)
```

## 日志输出示例

```
2026-04-03 12:17:55 - bjdc_data - INFO - 开始获取北京单场数据...
2026-04-03 12:17:56 - bjdc_data - INFO - 当前期数：26042
2026-04-03 12:17:56 - bjdc_data - INFO - 处理 26042 期联赛和比赛数据...
2026-04-03 12:17:57 - bjdc_data - INFO - 新增比赛：阿德莱德联 vs 奥克兰 FC (联赛：澳大利亚超级联赛)
...
2026-04-03 12:18:00 - bjdc_data - INFO - 获取 26042 期总进球数据...
2026-04-03 12:18:05 - bjdc_data - INFO - 总进球数据处理完成，更新 97 场
2026-04-03 12:18:05 - bjdc_data - INFO - 获取 26042 期比分数据...
2026-04-03 12:18:10 - bjdc_data - INFO - 比分数据处理完成，更新 97 场
2026-04-03 12:18:10 - bjdc_data - INFO - 北京单场数据采集完成
```

## 待完善功能

1. **胜平负赔率**
   - 目前未单独保存（北京单场通常通过让球计算）
   - 如需保存，可从网页中提取并保存到 `bjdc_spf_odds` 表

2. **让球胜平负赔率**
   - 当前网页结构中可能包含让球信息
   - 可在后续版本中完善提取和保存逻辑

3. **半全场赔率**
   - 网页中可能有相关数据
   - 可根据需求决定是否采集

## 总结

本次修复完成了三个主要任务：
1. ✅ 统一并完善了联赛处理逻辑
2. ✅ 修复了数据库模型的外键关系定义
3. ✅ 实现了完整的赔率数据保存功能

所有功能已通过实际运行测试和数据库验证，可以正常采集和保存北京单场比赛数据及赔率信息。
