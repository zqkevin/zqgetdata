# 日志系统说明

## 日志文件结构

从 2026-04-27 开始，日志系统采用**统一存储 + 按级别分离**的设计：

### 目录结构

```
app/log/{YYYY-MM}/
├── info.log        # 所有模块的 INFO 级别日志
├── warning.log     # 所有模块的 WARNING 级别日志
└── error.log       # 所有模块的 ERROR 和 CRITICAL 级别日志
```

### 日志格式

每条日志都包含模块标识，方便区分来源：

```
{时间} - {模块名称} - {级别} - {消息内容}
```

示例：
```
2026-04-27 07:43:18 - lottery_data - INFO - 开始更新最新彩票数据...
2026-04-27 07:43:18 - tczq_data - INFO - 开始获取比赛数据...
2026-04-27 07:43:18 - bjdc_data - WARNING - API返回数据为空
2026-04-27 07:43:18 - jcbk_data - ERROR - 网络请求超时
```

### 模块标识

| 模块标识 | 说明 |
|---------|------|
| `tczq_data` | 体彩足球数据 |
| `bjdc_data` | 北京单场数据 |
| `jcbk_data` | 竞彩篮球数据 |
| `lottery_data` | 数字彩票数据 |
| `api_request` | API 请求日志 |

### 日志级别说明

- **INFO**: 正常业务流程信息（数据采集、保存成功等）
- **WARNING**: 警告信息（数据已存在、API 返回空数据等）
- **ERROR**: 错误信息（数据库错误、网络异常等）
- **CRITICAL**: 严重错误（会记录到 error.log）

### 使用示例

#### 查看所有模块的正常流程
```bash
# 查看本月所有 INFO 日志
Get-Content app\log\2026-04\info.log -Tail 50
```

#### 只查看某个模块的日志
```bash
# 使用 Select-String 过滤特定模块
Get-Content app\log\2026-04\info.log | Select-String "lottery_data"
```

#### 查看所有错误
```bash
# 直接查看 error.log，包含所有模块的错误
Get-Content app\log\2026-04\error.log -Tail 20
```

#### 实时监控错误
```bash
# PowerShell 实时跟踪错误日志
Get-Content app\log\2026-04\error.log -Wait -Tail 10
```

### 优势

1. ✅ **集中管理**：所有模块的日志在同一个目录下，便于查找
2. ✅ **快速定位问题**：只需查看 error.log 即可发现所有错误
3. ✅ **减少干扰**：查看正常流程时不会被警告和错误信息干扰
4. ✅ **便于监控**：可以单独监控 error.log 文件大小或内容变化
5. ✅ **灵活过滤**：通过模块标识可以轻松过滤出特定模块的日志
6. ✅ **性能优化**：不同级别的日志写入不同的文件，减少锁竞争

### 日志清理

系统会自动清理 6 个月前的日志文件夹（包括 info/warning/error 三个文件）。

手动清理：
```python
from app.log import cleanup_old_logs
cleanup_old_logs(months_to_keep=3)  # 只保留最近 3 个月的日志
```

### 旧日志文件

旧的按模块分文件夹的结构（如 `app/log/lottery/2026-04/lottery_data.log`）是升级前生成的，可以安全删除或保留作为历史参考。
