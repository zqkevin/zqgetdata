# SportteryAPI 使用文档

## 概述

`SportteryAPI` 是中国体育彩票竞彩 API 调用类，提供足球、篮球和数字彩票的接口调用和数据清洗整理功能。

## 快速开始

```python
from app.common.req_sporttery_api import SportteryAPI

# 初始化 API 客户端
api = SportteryAPI()

# 使用各种 API 方法...

# 关闭会话
api.close()
```

---

## 足球相关 API

### 1. 获取足球比赛列表

**方法**: `get_football_match_list(pool_codes=None, channel="c")`

**参数**:
- `pool_codes` (List[str], 可选): 投注玩法代码列表，默认为 `['hhad', 'had', 'hafu', 'crs', 'ttg']`
  - `hhad`: 混合过关
  - `had`: 胜平负
  - `hafu`: 半全场
  - `crs`: 比分
  - `ttg`: 总进球
- `channel` (str, 可选): 渠道标识，默认为 `"c"`

**返回值格式**:
```python
{
    'match_info_list': [
        {
            'matchId': '2039062',           # 比赛ID
            'matchNum': '周一001',          # 比赛编号
            'matchDate': '2024-01-01',      # 比赛日期
            'matchTime': '20:00',           # 比赛时间
            'leagueName': '英超',           # 联赛名称
            'homeTeam': '曼联',             # 主队名称
            'awayTeam': '利物浦',           # 客队名称
            'poolCode': 'hhad',             # 玩法代码
            'odds': [...]                   # 赔率信息
        }
    ],
    'match_date_list': ['2024-01-01', '2024-01-02'],  # 比赛日期列表
    'league_list': [                        # 联赛列表
        {
            'leagueId': '1001',
            'leagueName': '英超'
        }
    ]
}
```

**示例**:
```python
result = api.get_football_match_list(pool_codes=['hhad', 'had'])
print(f"共有 {len(result['match_info_list'])} 场比赛")
```

---

### 2. 获取足球比赛赛果

**方法**: `get_football_match_result(match_begin_date=None, match_end_date=None)`

**参数**:
- `match_begin_date` (str, 可选): 比赛开始日期，格式为 `YYYY-MM-DD`
- `match_end_date` (str, 可选): 比赛结束日期，格式为 `YYYY-MM-DD`

**返回值格式**: List[Dict]

```python
[
    {
        'matchId': '2039062',               # 比赛ID
        'matchNum': '周一001',              # 比赛编号
        'matchDate': '2024-01-01',          # 比赛日期
        'homeTeam': '曼联',                 # 主队名称
        'allHomeTeam': '曼彻斯特联',        # 主队全称
        'awayTeam': '利物浦',               # 客队名称
        'allAwayTeam': '利物浦',            # 客队全称
        'homeScore': '2',                   # 主队得分（已结束）或 'N/A'/'取消'
        'awayScore': '1',                   # 客队得分（已结束）或 'N/A'/'取消'
        'halfHomeScore': '1',               # 半场主队得分
        'halfAwayScore': '0',               # 半场客队得分
        'matchResultStatus': '2',           # 比赛状态：2=已结束
        'leagueName': '英超',               # 联赛名称
        'leagueNameAbbr': 'EPL'             # 联赛简称
    }
]
```

**示例**:
```python
# 获取指定日期范围的赛果
results = api.get_football_match_result(
    match_begin_date='2024-01-01',
    match_end_date='2024-01-07'
)

for match in results:
    print(f"{match['matchNum']} {match['homeTeam']} {match['homeScore']}:{match['awayScore']} {match['awayTeam']}")
```

---

### 3. 获取足球赔率历史

**方法**: `get_football_match_odds_history(pool_codes=None, matchId=None)`

**参数**:
- `pool_codes` (List[str], 可选): 投注玩法代码列表，默认为 `['hhad', 'had']`
- `matchId` (str, 必填): 比赛ID

**返回值格式**: Dict

```python
{
    'matchId': '2039062',
    'poolOddsList': [
        {
            'poolCode': 'hhad',
            'oddsList': [
                {
                    'updateTime': '2024-01-01 10:00:00',  # 更新时间
                    'homeWin': '2.10',                     # 主胜赔率
                    'draw': '3.20',                        # 平局赔率
                    'awayWin': '3.50'                      # 客胜赔率
                }
            ]
        }
    ]
}
```

**示例**:
```python
odds_history = api.get_football_match_odds_history(
    pool_codes=['hhad'],
    matchId='2039062'
)
```

---

### 4. 搜索足球赔率

**方法**: `search_football_some_odds(match_id=None, h=None, a=None, d=None, league_id=None, homeTeamId=None, awayTeamId=None)`

**参数**:
- `match_id` (str, 可选): 比赛ID
- `h` (str, 可选): 让球数（主队）
- `a` (str, 可选): 参数a
- `d` (str, 可选): 参数d
- `league_id` (str, 可选): 联赛ID
- `homeTeamId` (str, 可选): 主队ID
- `awayTeamId` (str, 可选): 客队ID

**返回值格式**: Dict

```python
{
    'matchInfo': {
        'matchId': '2039062',
        'homeTeam': '曼联',
        'awayTeam': '利物浦',
        'matchTime': '2024-01-01 20:00:00'
    },
    'oddsList': [
        {
            'poolCode': 'hhad',
            'letNum': '-1',                  # 让球数
            'homeWin': '2.10',
            'draw': '3.20',
            'awayWin': '3.50',
            'singleFixed': '0'               # 是否单关固定
        }
    ]
}
```

**示例**:
```python
# 通过比赛ID查询
odds = api.search_football_some_odds(match_id='2039062')

# 通过球队ID查询
odds = api.search_football_some_odds(
    homeTeamId='10001',
    awayTeamId='10002'
)
```

---

### 5. 获取投注支持率（已废弃）

**方法**: `get_support_rate(match_id=None)`

**注意**: 此接口当前不可用，建议从网页抓取支持率数据。

**参数**:
- `match_id` (str, 可选): 比赛ID

**返回值**: 空字典 `{}`

---

## 篮球相关 API

### 1. 获取篮球比赛列表

**方法**: `get_basketball_match_list(client_code="3001")`

**参数**:
- `client_code` (str, 可选): 客户端代码，默认为 `"3001"`

**返回值格式**: pandas.DataFrame

DataFrame 包含以下列：
- `matchId`: 比赛ID
- `matchNum`: 比赛编号（如"周一301"）
- `matchNumStr`: 比赛编号字符串
- `matchNumDate`: 比赛编号日期
- `matchWeek`: 星期
- `matchDate`: 比赛日期
- `matchTime`: 比赛时间
- `leagueId`: 联赛ID
- `leagueName`: 联赛名称
- `homeTeamName`: 主队名称
- `awayTeamName`: 客队名称
- `matchStatus`: 比赛状态
- `sellStatus`: 销售状态（1=销售中，0=未销售）

**示例**:
```python
df = api.get_basketball_match_list()
print(f"共有 {len(df)} 场比赛")
print(df[['matchNum', 'homeTeamName', 'awayTeamName', 'matchTime']])
```

---

### 2. 获取篮球比赛计算器信息

**方法**: `get_basketball_match_calculator(pool_codes, channel="c")`

**参数**:
- `pool_codes` (List[str]): 投注玩法代码列表
  - `hilo`: 大小分
  - `spf`: 胜负
  - `rfsf`: 让分胜负
  - `sfc`: 胜分差
- `channel` (str, 可选): 渠道标识，默认为 `"c"`

**返回值格式**: Dict

```python
{
    'matchInfoList': [
        {
            'matchId': '3039062',
            'matchNum': '周一301',
            'leagueName': 'NBA',
            'homeTeamName': '湖人',
            'awayTeamName': '勇士',
            'matchTime': '2024-01-01 10:00:00',
            'subMatchList': [              # 子比赛列表（不同玩法）
                {
                    'matchId': '3039062',
                    'poolCode': 'hilo',
                    'preScore': '220.5',   # 预设分数
                    'bigOdds': '1.75',     # 大分赔率
                    'smallOdds': '1.75'    # 小分赔率
                }
            ]
        }
    ]
}
```

**示例**:
```python
calculator_data = api.get_basketball_match_calculator(['hilo', 'spf'])
```

---

### 3. 获取篮球比赛赛果

**方法**: `get_basketball_match_results(match_begin_date=None, match_end_date=None)`

**参数**:
- `match_begin_date` (str, 可选): 比赛开始日期，格式为 `YYYY-MM-DD`
- `match_end_date` (str, 可选): 比赛结束日期，格式为 `YYYY-MM-DD`

**返回值格式**: List[Dict]

```python
[
    {
        'matchId': '3039062',               # 比赛ID
        'matchNum': '周一301',              # 比赛编号
        'matchNumStr': '301',               # 比赛编号字符串
        'matchDate': '2024-01-01',          # 比赛日期
        'matchTime': '10:00',               # 比赛时间
        'homeTeam': '湖人',                 # 主队名称
        'allHomeTeam': '洛杉矶湖人',        # 主队全称
        'awayTeam': '勇士',                 # 客队名称
        'allAwayTeam': '金州勇士',          # 客队全称
        'homeTeamId': '20001',              # 主队ID
        'awayTeamId': '20002',              # 客队ID
        'homeScore': 110,                   # 主队得分
        'awayScore': 105,                   # 客队得分
        'leagueName': 'NBA',                # 联赛名称
        'leagueNameAbbr': 'NBA',            # 联赛简称
        'leagueId': '2001',                 # 联赛ID
        'status': '2',                      # 状态：2=已结束
        'poolStatus': 'Payout'              # 派奖状态
    }
]
```

**示例**:
```python
results = api.get_basketball_match_results(
    match_begin_date='2024-01-01',
    match_end_date='2024-01-07'
)

for match in results:
    print(f"{match['matchNum']} {match['homeTeam']} {match['homeScore']}:{match['awayScore']} {match['awayTeam']}")
```

---

## 数字彩票相关 API

### 1. 获取数字彩票开奖信息

**方法**: `get_digital_lottery_info(lottery_type, term_flag=0)`

**参数**:
- `lottery_type` (str): 彩票类型
  - `pl3`: 排列3
  - `pl5`: 排列5
  - `dlt`: 大乐透
  - `qxc`: 七星彩
- `term_flag` (int, 可选): 期号标识，0表示最近一期，默认为 0

**返回值格式**: Dict

```python
{
    'lotteryDrawNum': '2024001',           # 期号
    'lotteryDrawDate': '2024-01-01',       # 开奖日期
    'lotteryDrawResult': '123',            # 开奖结果（排列3/5）
    'frontZone': '01 02 03 04 05',         # 前区号码（大乐透）
    'backZone': '06 07',                   # 后区号码（大乐透）
    'prizePool': '500000000',              # 奖池金额
    'salesAmount': '300000000'             # 销售额
}
```

**示例**:
```python
# 获取最新一期大乐透
dlt_info = api.get_digital_lottery_info('dlt')
print(f"期号: {dlt_info['lotteryDrawNum']}")
print(f"开奖结果: {dlt_info['frontZone']} + {dlt_info['backZone']}")

# 获取排列5
pl5_info = api.get_digital_lottery_info('pl5')
print(f"排列5开奖结果: {pl5_info['lotteryDrawResult']}")
```

---

### 2. 获取数字彩票历史开奖

**方法**: `get_digital_lottery_history(lottery_type, page_no=1, page_size=30)`

**参数**:
- `lottery_type` (str): 彩票类型（pl3, pl5, dlt, qxc）
- `page_no` (int, 可选): 页码，默认第 1 页
- `page_size` (int, 可选): 每页条数，默认 30 条

**返回值格式**: Dict

```python
{
    'total': 1000,                          # 总记录数
    'pageNo': 1,                            # 当前页码
    'pageSize': 30,                         # 每页条数
    'pages': 34,                            # 总页数
    'result': [                             # 开奖结果列表
        {
            'lotteryDrawNum': '2024001',    # 期号
            'lotteryDrawDate': '2024-01-01',# 开奖日期
            'lotteryDrawResult': '123',     # 开奖结果
            'prizeDetails': [...]           # 奖项详情
        }
    ]
}
```

**示例**:
```python
# 获取大乐透最近30期历史
history = api.get_digital_lottery_history('dlt', page_no=1, page_size=30)
print(f"共 {history['total']} 期数据")

for item in history['result']:
    print(f"期号: {item['lotteryDrawNum']}, 开奖日期: {item['lotteryDrawDate']}")
```

---

### 3. 批量获取多种彩票信息

**方法**: `get_multi_lottery_data(lottery_types)`

**参数**:
- `lottery_types` (List[str]): 彩票类型列表，如 `['pl3', 'pl5', 'dlt', 'qxc']`

**返回值格式**: Dict[str, Dict]

```python
{
    'pl3': {
        'lotteryDrawNum': '2024001',
        'lotteryDrawDate': '2024-01-01',
        'lotteryDrawResult': '123'
    },
    'pl5': {
        'lotteryDrawNum': '2024001',
        'lotteryDrawDate': '2024-01-01',
        'lotteryDrawResult': '12345'
    },
    'dlt': {
        'lotteryDrawNum': '2024001',
        'lotteryDrawDate': '2024-01-01',
        'frontZone': '01 02 03 04 05',
        'backZone': '06 07'
    },
    'qxc': {
        'lotteryDrawNum': '2024001',
        'lotteryDrawDate': '2024-01-01',
        'lotteryDrawResult': '1234567'
    }
}
```

**示例**:
```python
# 一次性获取所有彩种的最新开奖
all_data = api.get_multi_lottery_data(['pl3', 'pl5', 'dlt', 'qxc'])

for lottery_type, data in all_data.items():
    if 'error' not in data:
        print(f"{lottery_type}: 期号 {data['lotteryDrawNum']}")
    else:
        print(f"{lottery_type}: {data['error']}")
```

---

## 通用说明

### 日期格式

所有日期参数支持多种格式输入，内部会自动转换为标准的 `YYYY-MM-DD` 格式：
- `2024-01-01`
- `2024/01/01`
- `2024.01.01`
- `20240101`

### 错误处理

所有 API 调用都可能抛出异常，建议使用 try-except 捕获：

```python
try:
    result = api.get_football_match_result(
        match_begin_date='2024-01-01',
        match_end_date='2024-01-07'
    )
except Exception as e:
    print(f"API 调用失败: {str(e)}")
```

常见错误：
- `网络请求错误`: 网络连接问题
- `JSON解析错误`: 响应数据格式错误
- `API请求失败`: API 返回错误信息

### 资源管理

使用完毕后务必关闭会话：

```python
api = SportteryAPI()
try:
    # 使用 API...
    pass
finally:
    api.close()
```

或使用上下文管理器模式（需自行实现）。

---

## 完整示例

```python
from app.common.req_sporttery_api import SportteryAPI

def main():
    api = SportteryAPI()
    
    try:
        # 1. 获取足球比赛列表
        print("=== 足球比赛列表 ===")
        football_list = api.get_football_match_list(['hhad'])
        print(f"共有 {len(football_list['match_info_list'])} 场比赛")
        
        # 2. 获取足球赛果
        print("\n=== 足球赛果 ===")
        football_results = api.get_football_match_result(
            match_begin_date='2024-01-01',
            match_end_date='2024-01-07'
        )
        for match in football_results[:5]:  # 只显示前5场
            print(f"{match['matchNum']} {match['homeTeam']} {match['homeScore']}:{match['awayScore']} {match['awayTeam']}")
        
        # 3. 获取篮球比赛列表
        print("\n=== 篮球比赛列表 ===")
        basketball_df = api.get_basketball_match_list()
        print(f"共有 {len(basketball_df)} 场比赛")
        
        # 4. 获取篮球赛果
        print("\n=== 篮球赛果 ===")
        basketball_results = api.get_basketball_match_results(
            match_begin_date='2024-01-01',
            match_end_date='2024-01-07'
        )
        for match in basketball_results[:5]:
            print(f"{match['matchNum']} {match['homeTeam']} {match['homeScore']}:{match['awayScore']} {match['awayTeam']}")
        
        # 5. 获取数字彩票信息
        print("\n=== 数字彩票 ===")
        lottery_data = api.get_multi_lottery_data(['dlt', 'pl5'])
        for lottery_type, data in lottery_data.items():
            if 'error' not in data:
                print(f"{lottery_type}: 期号 {data['lotteryDrawNum']}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        api.close()

if __name__ == "__main__":
    main()
```

---

## 注意事项

1. **请求频率**: 请控制 API 调用频率，避免被限制
2. **数据时效性**: API 返回的数据可能存在延迟，以实际开奖为准
3. **比赛状态**: 未结束的比赛比分可能为 `'N/A'`，取消的比赛比分为 `'取消'`
4. **分页处理**: 赛果查询会自动处理分页，无需手动处理
5. **日志记录**: 所有关键操作都会记录日志，可通过 `app.log.logger` 查看

---

## 版本信息

- **创建日期**: 2024
- **最后更新**: 2026-04-15
- **API 基础 URL**:
  - 足球: `https://webapi.sporttery.cn/gateway/uniform/football/`
  - 篮球: `https://webapi.sporttery.cn/gateway/uniform/basketball/`
  - 数字彩票: `https://webapi.sporttery.cn/gateway/lottery/`
