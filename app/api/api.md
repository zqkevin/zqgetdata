# API接口文档

## 概述
本项目提供了彩票数据相关的API接口，包括足球、篮球和数字彩票的数据获取。

## 接口列表

### /api/v1/football/match
- 请求方式：GET
- 说明：获取足球比赛数据
- 请求参数：
  | 字段名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | page   | int  | 否   | 页码，默认1 |
  | size   | int  | 否   | 每页条数，默认10 |
  | league | str  | 否   | 联赛名称 |
  | date   | str  | 否   | 比赛日期，格式YYYY-MM-DD |
- 返回格式：
  | 字段名 | 类型 | 说明 |
  |--------|------|------|
  | code   | int  | 状态码（200成功，500失败） |
  | data   | list | 比赛列表 |
  | msg    | str  | 提示信息 |
- 调用示例：
  curl -X GET "http://127.0.0.1:8000/api/v1/football/match?page=1&size=10" -H "Authorization: Bearer {token}"

### /api/v1/basketball/match
- 请求方式：GET
- 说明：获取篮球比赛数据
- 请求参数：
  | 字段名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | page   | int  | 否   | 页码，默认1 |
  | size   | int  | 否   | 每页条数，默认10 |
  | league | str  | 否   | 联赛名称 |
  | date   | str  | 否   | 比赛日期，格式YYYY-MM-DD |
- 返回格式：
  | 字段名 | 类型 | 说明 |
  |--------|------|------|
  | code   | int  | 状态码（200成功，500失败） |
  | data   | list | 比赛列表 |
  | msg    | str  | 提示信息 |
- 调用示例：
  curl -X GET "http://127.0.0.1:8000/api/v1/basketball/match?page=1&size=10" -H "Authorization: Bearer {token}"

### /api/v1/lottery/digital
- 请求方式：GET
- 说明：获取数字彩票数据
- 请求参数：
  | 字段名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | page   | int  | 否   | 页码，默认1 |
  | size   | int  | 否   | 每页条数，默认10 |
  | type   | str  | 否   | 彩票类型，如"qxc"表示七星彩 |
  | term   | str  | 否   | 期号 |
- 返回格式：
  | 字段名 | 类型 | 说明 |
  |--------|------|------|
  | code   | int  | 状态码（200成功，500失败） |
  | data   | list | 彩票数据列表 |
  | msg    | str  | 提示信息 |
- 调用示例：
  curl -X GET "http://127.0.0.1:8000/api/v1/lottery/digital?type=qxc&term=2024001" -H "Authorization: Bearer {token}"

### /api/v1/lottery/result
- 请求方式：GET
- 说明：获取彩票开奖结果
- 请求参数：
  | 字段名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | type   | str  | 是   | 彩票类型，如"qxc"表示七星彩 |
  | term   | str  | 否   | 期号，不填则返回最新一期 |
- 返回格式：
  | 字段名 | 类型 | 说明 |
  |--------|------|------|
  | code   | int  | 状态码（200成功，500失败） |
  | data   | dict | 开奖结果数据 |
  | msg    | str  | 提示信息 |
- 调用示例：
  curl -X GET "http://127.0.0.1:8000/api/v1/lottery/result?type=qxc&term=2024001" -H "Authorization: Bearer {token}"