#!/bin/bash
# 修复tczq_result.py中home_name未定义的问题

FILE="/root/py_program/zqget/app/crawler/tczq_result.py"

# 在 matched_count += 1 之后添加队名获取逻辑
sed -i '/matched_count += 1/a\                # 确保 home_name 和 away_name 已定义（用于日志输出）\n                if not home_name or not away_name:\n                    home_name = result_data.get("allHomeTeam") or result_data.get("homeTeam", "未知")\n                    away_name = result_data.get("allAwayTeam") or result_data.get("awayTeam", "未知")' "$FILE"

echo "修复完成！"
