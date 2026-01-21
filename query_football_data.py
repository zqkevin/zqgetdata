# -*- coding: utf-8 -*-
"""
查询数据库中的足球数据记录并打印出来
"""
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from app.database import localdb
from app.database.tczq_models import TczqMatch, TczqLeague

def query_football_records():
    """
    查询足球数据记录并打印
    """
    print("=== 查询足球数据记录开始 ===")
    
    try:
        # 查询所有足球比赛记录
        matches = localdb.query(TczqMatch).all()
        
        print(f"\n总共查询到 {len(matches)} 条足球比赛记录：")
        print("=" * 100)
        
        # 按联赛分组统计
        league_stats = {}
        for match in matches:
            league_name = match.league.league_name if match.league else "未知联赛"
            if league_name not in league_stats:
                league_stats[league_name] = 0
            league_stats[league_name] += 1
        
        print("\n各联赛比赛数量统计：")
        for league_name, count in league_stats.items():
            print(f"{league_name}: {count} 场")
        print("=" * 100)
        
        # 按比赛日期分组统计
        date_stats = {}
        for match in matches:
            if match.match_date not in date_stats:
                date_stats[match.match_date] = 0
            date_stats[match.match_date] += 1
        
        print("\n各日期比赛数量统计：")
        for date, count in sorted(date_stats.items()):
            print(f"{date}: {count} 场")
        print("=" * 100)
        
        # 详细比赛信息
        print("\n详细比赛信息：")
        for i, match in enumerate(matches, 1):
            # 获取联赛名称
            league_name = match.league.league_name if match.league else "未知联赛"
            
            # 格式化输出
            print(f"[{i}]")
            print(f"比赛ID: {match.match_id}")
            print(f"比赛编号: {match.match_num_str} (数字编号: {match.match_num})")
            print(f"比赛时间: {match.match_date} {match.match_time}")
            print(f"联赛: {league_name}")
            print(f"对阵双方: {match.home_team_abb_name} vs {match.away_team_abb_name}")
            print(f"主队全称: {match.home_team_all_name}")
            print(f"客队全称: {match.away_team_all_name}")
            print(f"投注状态: 单场-{match.betting_single}, 串关-{match.betting_all_up}")
            
            # 比赛状态中文解释
            status_dict = {0: "未开始", 1: "赛果已记录", 2: "赛果获取失败", 3: "比赛已取消", 4: "其他"}
            status_text = status_dict.get(match.status, f"未知状态({match.status})")
            print(f"比赛状态: {status_text}")
            
            print(f"创建时间: {match.created_at}")
            print(f"更新时间: {match.updated_at}")
            print("-" * 100)
            
    except Exception as e:
        print(f"查询足球数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        localdb.close()
    
    print("=== 查询足球数据记录结束 ===")

if __name__ == "__main__":
    query_football_records()