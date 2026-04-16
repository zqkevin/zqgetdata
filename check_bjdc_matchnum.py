# -*- coding: utf-8 -*-
"""
检查数据库中 bjdc 比赛的 matchNum 格式
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import localdb, BjdcMatch
from datetime import datetime, timedelta

# 查询一些 bjdc 比赛
matches = localdb.query(BjdcMatch).filter(
    BjdcMatch.status.in_([0, 1])
).limit(20).all()

print("=" * 80)
print("BJDC 比赛 matchNum 格式分析")
print("=" * 80)

for i, match in enumerate(matches, 1):
    home_name = match.home_team.team_full_name if match.home_team else '未知'
    away_name = match.away_team.team_full_name if match.away_team else '未知'
    match_date = match.match_time.strftime('%Y-%m-%d') if match.match_time else '未知'
    
    print(f"\n{i}. [{match_date}] {home_name} vs {away_name}")
    print(f"   match_id: {match.match_id}")
    print(f"   remark: {match.remark[:50] if match.remark else 'None'}...")

print("\n" + "=" * 80)
print("结论:")
print("=" * 80)
print("BJDC 数据库中没有 matchNum 字段")
print("需要通过其他方式匹配，比如队名 + 日期")
