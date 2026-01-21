## webapi.sporttery.cn API 文档

### 1. 通用信息

#### 基本请求头
```
accept: application/json, text/javascript, */*; q=0.01
accept-encoding: gzip, deflate, br, zstd
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
origin: https://www.sporttery.cn
pragma: no-cache
referer: https://www.sporttery.cn/
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Content-Type: application/json;charset=UTF-8
```

#### 通用响应格式
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {},
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

### 2. 足球相关接口

#### 2.1 足球比赛列表接口（football/info）

##### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/uniform/football/info`
- **请求方式**：GET
- **功能描述**：获取足球比赛列表信息

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| poolCode | string | 是 | 投注玩法代码，支持多个值用逗号分隔 | hhad,had |
| channel | string | 是 | 渠道标识 | c |

##### 玩法代码说明
- **hhad**：让球胜平负
- **had**：胜平负
- **hafu**：半全场胜平负
- **crs**：比分玩法
- **ttg**：总进球数

##### 返回数据结构
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "matchInfoList": [
      {
        "businessDate": "2026-01-07",
        "subMatchList": [
          {
            "matchId": 2036740,
            "matchNum": 4001,
            "matchNumDate": "20260107",
            "matchNumStr": "周四001",
            "matchStatus": "Selling",
            "matchDate": "2026-01-08",
            "matchTime": "00:30:00",
            "matchWeek": "周四",
            "businessDate": "2026-01-07",
            "taxDateNo": "2601071",
            "leagueId": 25,
            "leagueCode": "EPL",
            "leagueAllName": "英格兰超级联赛",
            "leagueAbbName": "英超",
            "homeTeamId": 1,
            "homeTeamCode": "ARS",
            "homeTeamAllName": "阿森纳",
            "homeTeamAbbName": "阿森纳",
            "homeTeamAbbEnName": "ARS",
            "homeRank": "1",
            "awayTeamId": 2,
            "awayTeamCode": "TOT",
            "awayTeamAllName": "托特纳姆热刺",
            "awayTeamAbbName": "热刺",
            "awayTeamAbbEnName": "TOT",
            "awayRank": "4",
            "baseHomeTeamId": 1,
            "baseAwayTeamId": 2,
            "lineNum": "1",
            "groupName": "",
            "matchName": "阿森纳VS热刺",
            "isHot": "Y",
            "isHide": "N",
            "backColor": "",
            "bettingSingle": 1,
            "bettingAllUp": 1,
            "sellStatus": 2,
            "had": {
              "h": "1.65",
              "d": "3.30",
              "a": "4.55",
              "hf": "0",
              "df": "0",
              "af": "0",
              "updateDate": "2026-01-07",
              "updateTime": "21:28:03"
            },
            "hhad": {
              "h": "3.45",
              "d": "3.40",
              "a": "1.85",
              "letNum": "-1",
              "hf": "0",
              "df": "0",
              "af": "0",
              "updateDate": "2026-01-07",
              "updateTime": "21:28:03"
            },
            "ttg": {
              "s0": "16.00",
              "s1": "5.85",
              "s2": "4.00",
              "s3": "3.15",
              "s4": "4.55",
              "s5": "8.20",
              "s6": "15.00",
              "s7": "50.00",
              "updateDate": "2026-01-06",
              "updateTime": "09:35:58"
            },
            "hafu": {
              "h3h3": "4.40",
              "h3h1": "7.50",
              "h3h0": "15.00",
              "h1h3": "6.00",
              "h1h1": "5.50",
              "h1h0": "8.50",
              "h0h3": "25.00",
              "h0h1": "12.50",
              "h0h0": "6.25",
              "updateDate": "2026-01-07",
              "updateTime": "21:28:03"
            },
            "crs": {
              "s00s00": "60.00",
              "s00s01": "15.00",
              "s00s02": "7.50",
              "s00s03": "5.00",
              "s01s00": "19.00",
              "s01s01": "5.50",
              "s01s02": "3.40",
              "s01s03": "2.60",
              "s02s00": "12.00",
              "s02s01": "4.20",
              "s02s02": "3.25",
              "s02s03": "3.15",
              "s03s00": "11.00",
              "s03s01": "5.85",
              "s03s02": "4.85",
              "updateDate": "2026-01-07",
              "updateTime": "21:28:03"
            },
            "vote": {},
            "poolList": [
              {
                "poolCode": "HAD",
                "poolStatus": "Selling",
                "single": 1,
                "allUp": 1
              },
              {
                "poolCode": "HHAD",
                "poolStatus": "Selling",
                "single": 1,
                "allUp": 1
              },
              {
                "poolCode": "HAFU",
                "poolStatus": "Selling",
                "single": 1,
                "allUp": 1
              },
              {
                "poolCode": "CRS",
                "poolStatus": "Selling",
                "single": 1,
                "allUp": 1
              },
              {
                "poolCode": "TTG",
                "poolStatus": "Selling",
                "single": 1,
                "allUp": 1
              }
            ],
            "oddsList": []
          }
        ]
      }
    ],
    "matchDateList": [
      {
        "businessDate": "2026-01-07",
        "businessDateCn": "周四"
      },
      {
        "businessDate": "2026-01-08",
        "businessDateCn": "周五"
      }
    ],
    "leagueList": [
      {
        "leagueId": 25,
        "leagueName": "英格兰超级联赛",
        "leagueNameAbbr": "英超"
      },
      {
        "leagueId": 40,
        "leagueName": "意大利甲级联赛",
        "leagueNameAbbr": "意甲"
      }
    ],
    "totalCount": 9,
    "lastUpdateTime": "2026-01-07 21:28:03"
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

##### 注意事项
- 该接口返回的 `matchInfoList` 是一个包含多个日期/时间段比赛集合的列表
- 每个日期/时间段比赛集合有一个 `subMatchList` 字段，这个字段才包含真正的比赛信息列表
- 比赛信息中包含了各种投注玩法的赔率数据

#### 2.2 足球比赛计算器接口（实时赔率）

##### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry`
- **请求方式**：GET
- **功能描述**：获取足球比赛的实时赔率和投注计算信息

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| poolCode | string | 是 | 投注玩法代码，支持多个值用逗号分隔 | hhad,had |
| channel | string | 是 | 渠道标识 | c |

##### 玩法代码说明
- **hhad**：让球胜平负
- **had**：胜平负
- **hafu**：半全场胜平负
- **crs**：比分玩法
- **ttg**：总进球数

##### 返回数据结构
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "vtoolsConfig": {},
    "matchInfoList": [
      {
        "businessDate": "2025-12-27",
        "subMatchList": [
          {
            "matchId": "2035566",
            "matchNum": "周六001",
            "matchNumStr": "周六001",
            "matchStatus": "Selling",
            "matchTime": "20:00:00",
            "homeTeamName": "主队名称",
            "awayTeamName": "客队名称",
            "homeTeamId": 123,
            "awayTeamId": 456,
            "homeTeamCode": "HT",
            "awayTeamCode": "AT",
            "leagueId": 25,
            "leagueName": "英格兰超级联赛",
            "hhad": "1.98,3.45,3.75",
            "had": "1.56,3.85,5.20",
            "sellStatus": 1,
            "backColor": "008888"
          }
        ]
      }
    ],
    "matchDateList": [
      {
        "businessDate": "2025-12-27",
        "businessDateCn": "周六"
      }
    ],
    "leagueList": [
      {
        "leagueId": 25,
        "leagueName": "英格兰超级联赛",
        "leagueNameAbbr": "英超"
      }
    ],
    "totalCount": 33,
    "lastUpdateTime": "2025-12-27 21:37:48"
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

#### 2.2 足球比赛结果接口

##### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/uniform/football/getUniformMatchResultV1.qry`
- **请求方式**：GET
- **功能描述**：获取足球比赛的赛果信息

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| channel | string | 是 | 渠道标识 | c |
| matchDate | string | 否 | 比赛日期，格式：YYYY-MM-DD | 2025-12-27 |

##### 返回数据结构
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "matchResultList": [
      {
        "matchId": "2035566",
        "matchNum": "周六001",
        "matchTime": "2025-12-27 20:00:00",
        "homeTeamName": "主队名称",
        "awayTeamName": "客队名称",
        "homeScore": "2",
        "awayScore": "1",
        "halfHomeScore": "1",
        "halfAwayScore": "0",
        "hhadResult": "3",
        "hadResult": "3",
        "hafuResult": "33",
        "ttgResult": "3",
        "crsResult": "2:1",
        "matchStatus": "End"
      }
    ]
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

##### 结果代码说明
- **hadResult**：胜平负结果（3=主胜，1=平局，0=客胜）
- **hhadResult**：让球胜平负结果（3=让球主胜，1=让球平局，0=让球客胜）
- **hafuResult**：半全场结果（前一位表示半场结果，后一位表示全场结果，3=胜，1=平，0=负）
- **ttgResult**：总进球数（0-9）
- **crsResult**：比分结果

#### 2.3 足球赔率搜索接口

##### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/uniform/football/searchOddsV1.qry`
- **请求方式**：GET
- **功能描述**：获取指定足球比赛的详细赔率信息

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| channel | string | 是 | 渠道标识 | c |
| type | string | 否 | 玩法类型 | hhad |
| matchId | string | 是 | 比赛ID | 2035566 |
| single | int | 否 | 是否单关（0=否，1=是） | 0 |

##### 返回数据结构
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "oddsList": [
      {
        "poolCode": "hhad",
        "poolName": "让球胜平负",
        "letNum": "-1",
        "h": "2.05",
        "d": "3.50",
        "a": "3.60",
        "spShow": "2.05,3.50,3.60",
        "spChange": "up",
        "maxBet": 50000,
        "minBet": 200
      }
    ],
    "poolInfos": {
      "hhad": {
        "poolCode": "hhad",
        "poolName": "让球胜平负",
        "maxBet": 50000,
        "minBet": 200
      }
    }
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

### 3. 篮球相关接口

#### 3.1 篮球比赛列表接口

##### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/uniform/basketball/getMatchListV2.qry`
- **请求方式**：GET
- **功能描述**：获取篮球比赛列表信息

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| clientCode | string | 是 | 客户端代码 | 3001 |

##### 返回数据结构
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "matchList": [
      {
        "matchId": "123456",
        "matchNum": "周日301",
        "matchTime": "2025-12-28 08:00:00",
        "homeTeamName": "主队名称",
        "awayTeamName": "客队名称",
        "homeTeamId": 789,
        "awayTeamId": 987,
        "leagueId": 1, 
        "leagueName": "NBA",
        "homeScore": "105",
        "awayScore": "98",
        "matchStatus": "End"
      }
    ]
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

#### 3.2 篮球赔率接口

##### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/uniform/basketball/getMatchCalculatorV1.qry`
- **请求方式**：GET
- **功能描述**：获取篮球比赛的实时赔率信息

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| poolCode | string | 是 | 投注玩法代码，支持多个值用逗号分隔 | hilo,spf |
| channel | string | 是 | 渠道标识 | c |

##### 篮球玩法代码说明
- **spf**：胜负
- **rfsf**：让分胜负
- **sfc**：胜分差
- **hilo**：大小分

##### 返回数据结构
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "vtoolsConfig": {},
    "matchInfoList": [
      {
        "businessDate": "2025-12-28",
        "subMatchList": [
          {
            "matchId": "2036460",
            "matchNum": 6318,
            "matchNumStr": "周六318",
            "matchStatus": "Selling",
            "matchTime": "09:00:00",
            "matchDate": "2025-12-28",
            "homeTeamName": "芝加哥公牛",
            "awayTeamName": "迈阿密热火",
            "homeTeamId": 21,
            "awayTeamId": 28,
            "leagueId": 1,
            "leagueName": "美国职业篮球联盟",
            "leagueCode": "NBA",
            "oddsList": [
              {
                "poolCode": "HILO",
                "goalLine": "+173.5",
                "goalLineValue": "+173.50",
                "h": "1.70",
                "a": "2.10",
                "poolId": 2174504,
                "updateTime": "19:54:41"
              }
            ],
            "poolList": [
              {
                "poolCode": "HILO",
                "poolStatus": "Selling",
                "fixedOddsgoalLine": "+173.5",
                "single": 0,
                "allUp": 1
              }
            ],
            "poolStatus": "Selling"
          }
        ]
      }
    ],
    "leaguesList": [
      {
        "leagueId": "1",
        "leagueName": "美国职业篮球联盟",
        "leagueNameAbbr": "美职篮"
      }
    ],
    "totalCount": 18,
    "lastUpdateTime": "2025-12-27 22:05:46"
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

##### 返回数据字段说明
- **oddsList**：赔率列表，包含各玩法的赔率信息
  - **poolCode**：玩法代码（HILO表示大小分）
  - **goalLine**：大小分盘口（+173.5表示总分盘口为173.5）
  - **h**：大分赔率（大于盘口为大分）
  - **a**：小分赔率（小于盘口为小分）
- **poolList**：玩法状态列表
  - **poolStatus**：销售状态（Selling表示销售中）
  - **single**：是否支持单关投注（0表示不支持，1表示支持）
  - **allUp**：是否支持串关投注（0表示不支持，1表示支持）

#### 3.3 篮球赛果与赔率分析

##### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/uniform/basketball/getMatchResultV1.qry`
- **请求方式**：GET
- **功能描述**：获取篮球比赛的赛果信息及对应的赔率分析

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| channel | string | 是 | 渠道标识 | c |
| matchDate | string | 否 | 比赛日期，格式：YYYY-MM-DD | 2025-12-27 |

##### 返回数据结构示例
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "matchResultList": [
      {
        "matchId": "2036450",
        "matchNum": "周六308",
        "matchTime": "2025-12-27 08:00:00",
        "homeTeamName": "布鲁克林篮网",
        "awayTeamName": "波士顿凯尔特人",
        "homeScore": "112",
        "awayScore": "108",
        "totalScore": "220",
        "spfResult": "3",
        "rfsfResult": "3",
        "sfcResult": "5",
        "hiloResult": "3",
        "oddsInfo": {
          "spf": "2.15,1.65",
          "rfsf": "1.80,1.90",
          "rfsfLetNum": "-4.5",
          "hilo": "1.75,2.05",
          "hiloPoint": "215.5"
        }
      }
    ]
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

##### 赛果与赔率分析说明
- **比分与赛果**：
  - **homeScore/awayScore**：主队/客队得分
  - **totalScore**：总分
  - **spfResult**：胜负结果（3=主胜，0=客胜）
  - **hiloResult**：大小分结果（3=大分，0=小分）

- **赔率分析**：
  - **spf**：胜负赔率（主队胜赔率,客队胜赔率）
  - **rfsf**：让分胜负赔率
  - **rfsfLetNum**：让分盘口
  - **hilo**：大小分赔率（大分赔率,小分赔率）
  - **hiloPoint**：大小分盘口

- **赛果与赔率对应关系**：
  例如，当比赛总分为220分，大小分盘口为215.5时：
  - 实际总分为220 > 215.5，所以大小分赛果为大分（hiloResult=3）
  - 对应的大分赔率为1.75，小分赔率为2.05
  - 如果投注了大分且比赛结果为大分，则可获得1.75倍的赔率收益

##### 注意事项
- 篮球赛果接口可能会返回空数据，尤其是在当天比赛尚未结束或官方数据尚未更新时
- 建议在调用该接口时添加异常处理逻辑，以应对空数据情况
- 篮球比赛计算器接口（大小分查询）工作正常，可稳定获取实时赔率数据

### 4. 投注配置信息接口

#### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/report/getVtoolsConfigV1.qry`
- **请求方式**：GET
- **功能描述**：获取中国体育彩票各种玩法的投注配置信息

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| configKey | string | 是 | 配置键名 | vtools:config:zc_app_loty_betshu |

#### 返回数据结构
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "zc_app_loty_betshu": [
      {
        "jczq": "1",
        "jclq": "1",
        "jczq_max": "50",
        "jclq_max": "50",
        "amountInfos": {
          "jczq": {
            "amount_limit": "",
            "amount_tips": ""
          }
        }
      }
    ]
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

### 5. 支持率查询接口

#### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/uniform/football/getSupportRateV1.qry`
- **请求方式**：GET
- **功能描述**：获取比赛投注支持率信息

#### 返回数据结构
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "matchList": [
      {
        "matchId": "2035566",
        "homeTeam": "主队名称",
        "awayTeam": "客队名称",
        "homeRate": "65.5",
        "drawRate": "20.3",
        "awayRate": "14.2"
      }
    ]
  },
  "emptyFlag": false,
  "dataFrom": null,
  "success": true
}
```

### 6. 主要彩票类型代码

#### 足球相关
- **`jczq`**：竞彩足球
- **`r9`**：足彩任选9场
- **`sfc`**：足球胜负彩
- **`cz6cbqcspf`**：6场半全场胜平负
- **`cz4cjq`**：4场进球彩

#### 篮球相关
- **`jclq`**：竞彩篮球
- **`jcmc`**：竞彩篮球让分

#### 数字彩
- **`pl3`**：排列3
- **`pl5`**：排列5
- **`dlt`**：大乐透
- **`qxc`**：七星彩
- **`jsx`**：江苏快3
- **`keno80x10`**：快乐8（80选10）

### 7. 接口使用注意事项

1. **请求头设置**：所有请求必须包含完整的User-Agent等头信息，否则会被拒绝访问
2. **频率限制**：请合理控制请求频率，避免过于频繁的API调用
3. **数据缓存**：建议对获取的数据进行适当缓存，减少重复请求
4. **错误处理**：请妥善处理API返回的错误信息，特别是errorCode不为0的情况
5. **参数验证**：在调用API前，请确保所有必填参数都已正确设置

### 9. 数字彩相关接口

#### 9.1 数字彩票开奖信息接口

##### 基本信息
- **接口地址**：`https://webapi.sporttery.cn/gateway/lottery/getDigitalDrawInfoV1.qry`
- **请求方式**：GET
- **功能描述**：获取数字彩票的开奖信息

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|------|------|--------|
| param | string | 是 | 参数组合，格式：彩票类型代码,期号标识<br>- 彩票类型代码：数字彩的唯一标识<br>- 期号标识：0表示最近一期 | 85,0 |
| isVerify | int | 否 | 是否需要验证<br>- 1：需要验证<br>- 0：不需要验证<br>- 经测试，此参数对返回结果无明显影响 | 1 |

##### 彩票类型代码说明

| 彩票类型 | 代码 |
|--------|-----|
| 超级大乐透 | 85 |
| 排列3 | 35 |
| 七星彩 | 04 |
| 排列5 | 350133 |

**注意**：
1. 代码35仅获取排列3数据，排列5需要使用单独的代码350133获取
2. 要同时获取多个彩种的数据，需要为每个彩种单独发起请求，而不是在一个请求中使用逗号分隔的多个参数

### 7.2 历史开奖列表API

#### 基本信息
- **接口地址**：https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry
- **请求方式**：GET
- **功能**：获取指定彩票的历史开奖记录列表

#### 请求参数
| 参数名 | 类型 | 必选 | 说明 |
|-------|------|------|------|
| gameNo | string | 是 | 彩票游戏编号，对应彩票类型代码说明中的代码 |
| provinceId | integer | 否 | 省份ID，0表示全国 |
| isVerify | integer | 否 | 是否需要验证，0或1 |
| termLimits | integer | 否 | 获取的期数限制 |

#### gameNo参数说明
gameNo参数用于指定要获取哪个彩种的历史开奖记录，与彩票类型代码一一对应：

| 彩票类型 | gameNo |
|--------|--------|
| 七星彩 | 04 |
| 排列3 | 35 |
| 超级大乐透 | 85 |
| 排列5 | 350133 |

#### 返回数据结构示例
```json
{
  "dataFrom": "",
  "emptyFlag": false,
  "errorCode": "0",
  "errorMessage": "处理成功",
  "success": true,
  "value": {
    "lastPoolDraw": {
      "lotteryDrawNum": "26002",
      "lotteryDrawResult": "3 4 5 5 9 8 9",
      "lotteryDrawTime": "2026-01-04",
      "lotteryGameName": "7星彩",
      "lotteryGameNum": "04",
      "poolBalanceAfterdraw": "295,392,103.95",
      "prizeLevelList": [
        {
          "awardType": 0,
          "group": "10",
          "lotteryCondition": "",
          "prizeLevel": "一等奖",
          "sort": 10,
          "stakeAmount": "5,000,000",
          "stakeCount": "1",
          "totalPrizeamount": "5,000,000"
        }
        // 更多奖级信息...
      ]
    },
    "list": [
      {
        "lotteryDrawNum": "26002",
        "lotteryDrawResult": "3 4 5 5 9 8 9",
        "lotteryDrawTime": "2026-01-04",
        "lotteryGameName": "7星彩",
        "lotteryGameNum": "04"
        // 更多开奖信息...
      }
      // 更多历史记录...
    ],
    "pageNo": 1,
    "pageSize": 10,
    "pages": 1,
    "total": 10
  }
}
```

#### 返回数据字段说明
| 字段名 | 类型 | 说明 |
|-------|------|------|
| lastPoolDraw | object | 最近一期的开奖信息 |
| list | array | 历史开奖记录列表 |
| pageNo | integer | 当前页码 |
| pageSize | integer | 每页记录数 |
| pages | integer | 总页数 |
| total | integer | 总记录数 |
| lotteryDrawNum | string | 开奖期号 |
| lotteryDrawResult | string | 开奖结果 |
| lotteryDrawTime | string | 开奖时间 |
| lotteryGameName | string | 彩票名称 |
| lotteryGameNum | string | 彩票游戏编号 |
| poolBalanceAfterdraw | string | 开奖后奖池金额 |
| prizeLevelList | array | 奖级信息列表 |

##### 返回数据结构示例
```json
{
  "errorCode": "0",
  "errorMessage": "处理成功",
  "value": {
    "dlt": {
      "drawPdfUrl": "https://pdf.sporttery.cn/28100/26001/26001.pdf",
      "lotteryGameName": "超级大乐透",
      "lotteryDrawNum": "26001",
      "lotteryDrawTime": "2026-01-03 21:20:19",
      "lotteryDrawResult": "07 09 23 27 32 02 08",
      "lotteryGameNum": "85",
      "poolBalanceAfterdraw": "1,500,000,000",
      "termList": ["26001", "25150", "25149"],
      "prizeLevelList": [
        {
          "awardType": 1,
          "prizeLevel": "一等奖",
          "stakeCount": "1",
          "totalPrizeamount": "5,000,000"
        }
      ]
    },
    "pls": {
      "drawPdfUrl": "https://pdf.sporttery.cn/28200/26004/26004.pdf",
      "lotteryGameName": "排列3",
      "lotteryDrawNum": "26004",
      "lotteryDrawTime": "2026-01-04 21:11:41",
      "lotteryDrawResult": "8 7 8",
      "lotteryGameNum": "35",
      "poolBalanceAfterdraw": "0",
      "prizeLevelList": [
        {
          "awardType": 0,
          "group": "10",
          "prizeLevel": "直选",
          "stakeAmount": "1,040",
          "stakeCount": "11,907",
          "totalPrizeamount": "12,383,280"
        }
      ]
    },
    "plw": {
      "drawPdfUrl": "https://pdf.sporttery.cn/28300/26004/26004.pdf",
      "lotteryGameName": "排列5",
      "lotteryDrawNum": "26004",
      "lotteryDrawTime": "2026-01-04 21:11:41",
      "lotteryDrawResult": "8 7 8 8 2",
      "lotteryGameNum": "350133",
      "poolBalanceAfterdraw": "311,336,191.78",
      "prizeLevelList": [
        {
          "awardType": 0,
          "group": "1010",
          "prizeLevel": "一等奖",
          "stakeAmount": "100,000",
          "stakeCount": "33",
          "totalPrizeamount": "3,300,000"
        }
      ]
    },
    "qxc": {
      "drawPdfUrl": "https://pdf.sporttery.cn/17100/26002/26002.pdf",
      "lotteryGameName": "7星彩",
      "lotteryDrawNum": "26002",
      "lotteryDrawTime": "2026-01-04 21:11:33",
      "lotteryDrawResult": "3 4 5 5 9 8 9",
      "lotteryGameNum": "04",
      "poolBalanceAfterdraw": "295,392,103.95",
      "prizeLevelList": [
        {
          "awardType": 0,
          "group": "10",
          "prizeLevel": "一等奖",
          "stakeAmount": "5,000,000",
          "stakeCount": "1",
          "totalPrizeamount": "5,000,000"
        }
      ]
    }
  },
  "emptyFlag": false,
  "dataFrom": "",
  "success": true
}
```

##### 返回字段说明
| 字段名 | 类型 | 说明 | 示例值 |
|-------|------|------|--------|
| value | object | 彩票数据集合，以彩票类型代码为键 | {"dlt": {...}, "pls": {...}, "plw": {...}, "qxc": {...}} |
| dlt | object | 超级大乐透数据 | {...} |
| pls | object | 排列3数据 | {...} |
| plw | object | 排列5数据 | {...} |
| qxc | object | 七星彩数据 | {...} |
| *.lotteryGameName | string | 彩票名称 | 超级大乐透/排列3/排列5/7星彩 |
| *.lotteryDrawNum | string | 期号 | 26001/26004 |
| *.lotteryDrawTime | string | 开奖时间 | 2026-01-03 21:20:19 |
| *.lotteryDrawResult | string | 开奖结果<br>- 超级大乐透：前区5个号码 后区2个号码<br>- 排列3：3个号码<br>- 排列5：5个号码<br>- 七星彩：7个号码 | 07 09 23 27 32 02 08 / 8 7 8 / 8 7 8 8 2 / 3 4 5 5 9 8 9 |
| *.lotteryGameNum | string | 彩票类型代码 | 85/35/350133/04 |
| *.poolBalanceAfterdraw | string | 奖池余额 | 1,500,000,000 / 0 / 311,336,191.78 |
| *.termList | array | 期号列表 | ["26001", "25150", "25149"] |
| *.prizeLevelList | array | 奖级列表 | [{"prizeLevel": "一等奖", "stakeCount": "1", ...}] |
| *.drawPdfUrl | string | 开奖公告PDF链接 | https://pdf.sporttery.cn/28100/26001/26001.pdf |
| *.lotterySaleBeginTime | string | 销售开始时间 | 2026-01-03 09:00:00 |
| *.lotterySaleEndtime | string | 销售结束时间 | 2026-01-03 20:00:00 |
| *.isGetKjpdf | int | 是否获取开奖PDF | 1 |
| *.lastPoolDraw | object | 上一期开奖数据 | {...} |
| *.lotteryEquipmentCount | int | 设备数量 | 0 |
| *.lotteryGamePronum | int | 游戏编号 | 0 |
| *.lotteryNotice | int | 公告标识 | 1 |
| *.lotteryNoticeShowFlag | int | 公告显示标识 | 1 |
| *.lotteryUnsortDrawresult | string | 未排序的开奖结果 | 07 09 23 27 32 02 08 |
| *.ruleType | int | 规则类型 | 0 |
| *.verify | int | 验证标识 | 1 |

### 8. 示例代码

#### Python示例
```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.sporttery.cn/'
}

# 获取足球实时赔率
def get_football_odds(pool_codes, channel='c'):
    url = 'https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry'
    params = {
        'poolCode': ','.join(pool_codes),
        'channel': channel
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# 获取足球赛果
def get_football_results(match_begin_date=None, match_end_date=None, league_id=None, page_size=30, page_no=1, is_fix=0, match_page=1, pc_or_wap=1):
    url = 'https://webapi.sporttery.cn/gateway/uniform/football/getUniformMatchResultV1.qry'
    params = {
        'channel': 'c',
        'pageSize': page_size,
        'pageNo': page_no,
        'isFix': is_fix,
        'matchPage': match_page,
        'pcOrWap': pc_or_wap
    }
    if match_begin_date:
        params['matchBeginDate'] = match_begin_date
    if match_end_date:
        params['matchEndDate'] = match_end_date
    if league_id:
        params['leagueId'] = league_id
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# 获取数字彩开奖信息
def get_digital_lottery_result(lottery_type, draw_num=0):
    """
    获取数字彩票开奖信息
    
    参数:
    lottery_type: 彩票类型代码(如85表示超级大乐透)
    draw_num: 期号标识(0表示最近一期)
    
    返回:
    response.json(): API响应数据
    """
    url = 'https://webapi.sporttery.cn/gateway/lottery/getDigitalDrawInfoV1.qry'
    params = {
        'param': f'{lottery_type},{draw_num}',
        'isVerify': 1
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# 使用示例
if __name__ == '__main__':
    # 获取足球胜平负和让球胜平负赔率
    odds_data = get_football_odds(['had', 'hhad'])
    print('足球赔率数据:', odds_data)
    
    # 获取指定日期范围的足球赛果
    # 示例：获取2026-01-09到2026-01-11的比赛结果
    results_data = get_football_results(match_begin_date='2026-01-09', match_end_date='2026-01-11')
    print('足球赛果数据:', results_data)
    
    # 数字彩票类型代码映射
    lottery_types = {
        85: ('超级大乐透', 'dlt'),
        35: ('排列3', 'pls'),
        350133: ('排列5', 'plw'),
        04: ('七星彩', 'qxc')
    }
    
    # 获取所有数字彩票的最近一期开奖信息
    for code, (name, key) in lottery_types.items():
        print(f"\n获取{name}({code})最近一期开奖信息:")
        lottery_data = get_digital_lottery_result(code)
        if lottery_data and lottery_data['errorCode'] == '0' and 'value' in lottery_data:
            lottery_data_obj = lottery_data['value'].get(key, {})
            if lottery_data_obj:
                print(f"  期号: {lottery_data_obj.get('lotteryDrawNum')}")
                print(f"  开奖时间: {lottery_data_obj.get('lotteryDrawTime')}")
                print(f"  开奖结果: {lottery_data_obj.get('lotteryDrawResult')}")
                print(f"  奖池余额: {lottery_data_obj.get('poolBalanceAfterdraw')}")
            else:
                print(f"  未获取到{name}数据")
        else:
            print(f"  获取{name}开奖信息失败")
```