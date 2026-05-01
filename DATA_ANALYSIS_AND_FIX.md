# 远程数据库数据完整性分析与修复方案

## 📊 检查结果总结

### 当前数据状态（2026-05-01 16:27）

| 数据类型 | 总记录数 | 状态分布 | 问题 |
|---------|---------|---------|------|
| TCZQ比赛 | 156场 | 未开赛:51, 状态8:95, 状态9:10 | ⚠️ 状态码不规范 |
| BJDC比赛 | 516场 | 未开赛:76, 状态8:440 | ⚠️ 状态码不规范 |
| TCBK比赛 | 55场 | - | ❌ 无赛果数据 |
| 数字彩票 | 24条开奖 | 0种类型 | ❌ 缺少类型定义 |

---

## 🔍 问题分析

### 1. 状态码使用问题 ⚠️

#### 现状
代码中使用了自定义状态码：
- `0`: 待开赛
- `1`: 进行中  
- `2`: 已完成
- `8`: 已获取赛果（完成状态标识）
- `9`: 异常（超过4天无结果）

#### 问题
数据库中大量比赛状态为8和9，而不是标准的0/1/2，这导致：
1. 状态统计不直观
2. 与常规理解不符（通常2表示已完成）
3. 查询过滤条件需要特殊处理

#### 根本原因
在`get_data/app/crawler/tczq_result.py`第436行：
```python
# 正常比赛：标记状态为8（已完成，已获取赛果）
match.status = 8
localdb.update(match, close=False)
```

以及在第99行标记异常比赛：
```python
# 标记为异常状态 (status=9)
match.status = 9
```

### 2. TCBK缺少赛果数据 ❌

#### 现状
- 55场比赛，0条赛果记录
- 篮球赛果API应该返回`status`字段

#### 可能原因
1. TCBK赛果采集功能未正常运行
2. 赛果匹配逻辑有问题
3. API返回的数据格式与预期不符

### 3. 数字彩票缺少类型定义 ❌

#### 现状
- 有24条开奖记录
- 但`digital_lottery_types`表为空

#### 影响
- 无法知道这些开奖记录属于哪种彩票
- 数据完整性受损

---

## 💡 修复方案

### 方案A：统一状态码为标准值（推荐）✅

将状态8和9改为标准的状态2（已完成），保留额外信息在其他字段中。

#### 优点
1. 状态码符合常规理解
2. 查询和统计更简单
3. 与其他系统兼容性好

#### 实施步骤

1. **修改状态码定义** (`get_data/app/common/match_status.py`)
```python
STATUS_DESC = {
    0: '待开赛',
    1: '进行中',
    2: '已完成',  # 合并原来的2和8
    3: '延期',
    4: '腰斩',
    5: '中断',
    9: '异常',    # 保留异常状态
}
```

2. **修改赛果保存逻辑** (`get_data/app/crawler/tczq_result.py`)
```python
# 第436行，改为：
match.status = 2  # 标准已完成状态
localdb.update(match, close=False)
```

3. **添加额外标识字段**（可选）
在`TczqMatch`模型中添加：
```python
result_fetched = Column(Boolean, default=False)  # 是否已获取赛果
result_fetched_at = Column(DateTime)  # 赛果获取时间
```

4. **更新现有数据**
```sql
UPDATE tczq_match SET status = 2 WHERE status = 8;
UPDATE bjdc_match SET status = 2 WHERE status = 8;
```

### 方案B：保持现状，优化文档和查询 ⚠️

保持状态8和9的使用，但：
1. 完善文档说明
2. 提供便捷的查询方法
3. 在前端/API层做状态转换

#### 缺点
- 状态码仍然不符合常规
- 需要额外的转换逻辑

---

## 🛠️ 具体修复操作

### 第一步：修复TCZQ和BJDC状态码

```bash
# 切换到master分支
git checkout master

# 修改 match_status.py
# 将状态8的含义从"已获取赛果"改为"已完成"的别名

# 修改 tczq_result.py 第436行
# match.status = 8  ->  match.status = 2

# 修改 bjdc_result.py 类似位置
```

### 第二步：修复TCBK赛果采集

检查`get_data/app/crawler/jcbk_result.py`：
1. 确认是否正确调用`get_basketball_match_results` API
2. 检查赛果匹配逻辑
3. 确认是否正确设置`status=2`

### 第三步：初始化数字彩票类型

创建脚本初始化彩票类型：
```python
lottery_types = [
    {'type_code': 'SSQ', 'type_name': '双色球', 'draw_days': [2, 4, 7]},
    {'type_code': 'DLT', 'type_name': '大乐透', 'draw_days': [1, 3, 6]},
    # ... 其他类型
]
```

### 第四步：更新现有数据

执行SQL更新：
```sql
-- TCZQ
UPDATE tczq_match SET status = 2 WHERE status = 8;

-- BJDC  
UPDATE bjdc_match SET status = 2 WHERE status = 8;

-- 验证
SELECT status, COUNT(*) FROM tczq_match GROUP BY status;
SELECT status, COUNT(*) FROM bjdc_match GROUP BY status;
```

---

## 📝 建议

1. **立即执行**：采用方案A统一状态码
2. **优先级**：
   - P0: 修复状态码（影响数据统计和展示）
   - P1: 修复TCBK赛果采集（数据缺失）
   - P2: 补充数字彩票类型（数据完整性）

3. **后续优化**：
   - 添加`result_fetched`字段明确标识赛果获取状态
   - 完善日志输出，便于排查问题
   - 添加数据质量监控告警

---

## ✅ 验收标准

修复后应满足：
1. TCZQ和BJDC比赛状态只使用0/1/2/3/4/5/9
2. 已结束比赛的status=2
3. TCBK有正常的赛果数据
4. 数字彩票有完整的类型定义
5. 数据查询和统计结果符合预期
