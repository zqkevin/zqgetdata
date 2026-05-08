import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'get_data'))

from app.crawler.jcbk import JcbkDataCollector
from datetime import datetime

print("=" * 100)
print("测试TCBK修复效果")
print("=" * 100)

collector = JcbkDataCollector()

# 获取比赛列表
print("\n1. 获取篮球比赛数据...")
try:
    result = collector.get_matches_with_odds()
    print(f"   采集完成")
    
    # 检查数据库中的数据
    from app.database import localdb, TcbkMatch
    
    # 查询最近更新的5场比赛
    recent_matches = localdb.query(TcbkMatch).order_by(TcbkMatch.updated_at.desc()).limit(5).all()
    
    print(f"\n2. 数据库中最近更新的5场比赛:")
    for i, match in enumerate(recent_matches, 1):
        print(f"\n   [{i}] Match ID: {match.match_id}")
        print(f"       比赛时间: {match.match_time} (类型: {type(match.match_time)})")
        print(f"       状态: {match.match_status}")
        print(f"       主队: {match.home_team_all_name}")
        print(f"       客队: {match.away_team_all_name}")
        
        # 验证match_time是否包含日期
        if match.match_time:
            if isinstance(match.match_time, str):
                has_date = '-' in match.match_time and len(match.match_time) > 10
            else:
                has_date = True
            print(f"       ✓ 包含日期: {has_date}")
        
        # 验证match_status不为None
        if match.match_status is not None:
            print(f"       ✓ 状态码有效: {match.match_status}")
        else:
            print(f"       ✗ 状态码为NULL!")
    
    # 统计整体情况
    total = localdb.query(TcbkMatch).count()
    null_status = localdb.query(TcbkMatch).filter(TcbkMatch.match_status == None).count()
    valid_time = localdb.query(TcbkMatch).filter(
        TcbkMatch.match_time != None,
        TcbkMatch.match_time.like('%-%')  # 包含日期格式
    ).count()
    
    print(f"\n3. 整体数据统计:")
    print(f"   总比赛数: {total}")
    print(f"   match_status为NULL: {null_status} ({null_status/total*100:.1f}%)" if total > 0 else "   无数据")
    print(f"   match_time包含日期: {valid_time} ({valid_time/total*100:.1f}%)" if total > 0 else "   无数据")
    
    if null_status == 0 and valid_time == total:
        print(f"\n✅ 修复成功！所有字段都正确设置")
    else:
        print(f"\n⚠️ 仍有问题需要修复")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
