# -*- coding: utf-8 -*-
"""
查询特定比赛的数据库记录
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import localdb, BjdcMatch
from datetime import datetime


def check_match_in_db(match_id=2039109):
    """检查比赛在数据库中的记录"""
    
    print("=" * 80)
    print(f"查询比赛 ID: {match_id}")
    print("=" * 80)
    
    # 1. 直接通过 match_id 查询
    match = localdb.query(BjdcMatch).filter_by(match_id=match_id).first()
    
    if match:
        print("\n✅ 找到比赛记录:")
        print(f"  比赛ID: {match.match_id}")
        print(f"  期数: {match.issue}")
        print(f"  比赛编号: {match.match_num_str}")
        print(f"  开赛时间: {match.match_time}")
        print(f"  状态: {match.status} (0=未开始, 1=已结束, 2=异常)")
        print(f"  备注: {match.remark or '无'}")
        
        home_name = match.home_team.team_full_name if match.home_team else '未知'
        away_name = match.away_team.team_full_name if match.away_team else '未知'
        print(f"  比赛: {home_name} vs {away_name}")
        
        league_name = match.league.league_name if match.league else '未知'
        print(f"  联赛: {league_name}")
        
        print(f"\n  创建时间: {match.created_at}")
        print(f"  更新时间: {match.updated_at}")
    else:
        print("\n❌ 数据库中未找到该比赛记录")
        
        # 2. 尝试通过日期和队名查找
        print("\n尝试通过日期和队名搜索...")
        
        # API 返回的比赛日期是 2026-04-15
        target_date = datetime(2026, 4, 15).date()
        
        matches_on_date = localdb.query(BjdcMatch).filter(
            BjdcMatch.match_time >= datetime.combine(target_date, datetime.min.time()),
            BjdcMatch.match_time < datetime.combine(target_date, datetime.max.time())
        ).all()
        
        print(f"\n{target_date} 共有 {len(matches_on_date)} 场比赛:")
        
        for m in matches_on_date:
            home = m.home_team.team_full_name if m.home_team else '未知'
            away = m.away_team.team_full_name if m.away_team else '未知'
            
            # 检查是否是目标比赛
            if '曼谷联' in home or '大阪钢巴' in away:
                print(f"\n  🔍 可能匹配的比赛:")
                print(f"    比赛ID: {m.match_id}")
                print(f"    开赛时间: {m.match_time}")
                print(f"    状态: {m.status}")
                print(f"    比赛: {home} vs {away}")
                print(f"    期数: {m.issue}")
                print(f"    备注: {m.remark or '无'}")


if __name__ == '__main__':
    try:
        check_match_in_db()
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
