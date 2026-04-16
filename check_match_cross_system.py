# -*- coding: utf-8 -*-
"""
检查比赛在 tczq 和 bjdc 两个系统中的记录
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import localdb, TczqMatch, BjdcMatch
from datetime import datetime


def check_match_in_both_systems():
    """检查比赛在两个系统中的记录"""
    
    print("=" * 80)
    print("检查曼谷联 vs 大阪钢巴 在两个系统中的记录")
    print("=" * 80)
    
    target_date = datetime(2026, 4, 15).date()
    
    # 1. 查询 tczq 系统
    print("\n【1】体彩足球 (tczq) 系统:")
    print("-" * 80)
    
    tczq_matches = localdb.query(TczqMatch).filter(
        TczqMatch.match_time >= datetime.combine(target_date, datetime.min.time()),
        TczqMatch.match_time < datetime.combine(target_date, datetime.max.time())
    ).all()
    
    tczq_target = None
    for m in tczq_matches:
        home = m.home_team.team_full_name if m.home_team else '未知'
        away = m.away_team.team_full_name if m.away_team else '未知'
        
        if '曼谷联' in home or '大阪钢巴' in away:
            tczq_target = m
            print(f"  ✅ 找到比赛:")
            print(f"    比赛ID: {m.match_id}")
            print(f"    开赛时间: {m.match_time}")
            print(f"    状态: {m.status}")
            print(f"    期数: {m.issue}")
            print(f"    比赛: {home} vs {away}")
            
            # 检查是否有赛果
            from app.database import TczqMatchResult
            result = localdb.query(TczqMatchResult).filter_by(match_id=m.match_id).first()
            if result:
                print(f"    📊 赛果记录:")
                print(f"      主队进球: {result.home_team_goals}")
                print(f"      客队进球: {result.away_team_goals}")
                print(f"      半场主队: {result.half_time_home_goals}")
                print(f"      半场客队: {result.half_time_away_goals}")
            else:
                print(f"    ❌ 无赛果记录")
            break
    
    if not tczq_target:
        print("  ❌ 未找到该比赛")
    
    # 2. 查询 bjdc 系统
    print("\n【2】北京单场 (bjdc) 系统:")
    print("-" * 80)
    
    bjdc_matches = localdb.query(BjdcMatch).filter(
        BjdcMatch.match_time >= datetime.combine(target_date, datetime.min.time()),
        BjdcMatch.match_time < datetime.combine(target_date, datetime.max.time())
    ).all()
    
    bjdc_target = None
    for m in bjdc_matches:
        home = m.home_team.team_full_name if m.home_team else '未知'
        away = m.away_team.team_full_name if m.away_team else '未知'
        
        if '曼谷联' in home or '大阪钢巴' in away:
            bjdc_target = m
            print(f"  ✅ 找到比赛:")
            print(f"    比赛ID: {m.match_id}")
            print(f"    开赛时间: {m.match_time}")
            print(f"    状态: {m.status}")
            print(f"    期数: {m.issue}")
            print(f"    比赛编号: {m.match_num_str}")
            print(f"    比赛: {home} vs {away}")
            
            # 检查是否有赛果
            from app.database import BjdcMatchResult
            result = localdb.query(BjdcMatchResult).filter_by(match_id=m.match_id).first()
            if result:
                print(f"    📊 赛果记录:")
                print(f"      主队进球: {result.home_team_goals}")
                print(f"      客队进球: {result.away_team_goals}")
                print(f"      半场主队: {result.half_time_home_goals}")
                print(f"      半场客队: {result.half_time_away_goals}")
            else:
                print(f"    ❌ 无赛果记录")
            break
    
    if not bjdc_target:
        print("  ❌ 未找到该比赛")
    
    # 3. 对比分析
    print("\n【3】对比分析:")
    print("-" * 80)
    
    if tczq_target and bjdc_target:
        print(f"  两个系统都有这场比赛")
        print(f"  tczq match_id: {tczq_target.match_id}")
        print(f"  bjdc match_id: {bjdc_target.match_id}")
        print(f"  ID 是否相同: {'是' if tczq_target.match_id == bjdc_target.match_id else '否'}")
        
        # 检查 API 返回的 matchId
        api_match_id = 2039109
        print(f"\n  API 返回的 matchId: {api_match_id}")
        print(f"  与 tczq match_id 匹配: {'是' if api_match_id == tczq_target.match_id else '否'}")
        print(f"  与 bjdc match_id 匹配: {'是' if api_match_id == bjdc_target.match_id else '否'}")
        
    elif tczq_target:
        print("  仅在 tczq 系统中存在")
    elif bjdc_target:
        print("  仅在 bjdc 系统中存在")
    else:
        print("  两个系统中都不存在")


if __name__ == '__main__':
    try:
        check_match_in_both_systems()
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
