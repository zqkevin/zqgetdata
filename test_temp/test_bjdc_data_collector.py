# -*- coding: utf-8 -*-
"""
测试北京单场数据采集器
验证联赛处理、球队处理和赔率保存功能
"""
import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from app.crawler.bjdc import BjdcDataCollector
from app.database import localdb, BjdcMatch, BjdcTotalGoalOdds, BjdcScoreOdds, League, Team

def test_bjdc_collector():
    """测试北京单场数据采集器"""
    print("=" * 60)
    print("Test BJDC Data Collector")
    print("=" * 60)
    
    # 1. 创建采集器
    print("\n1. 创建采集器...")
    collector = BjdcDataCollector()
    print("✓ 采集器创建成功")
    
    # 2. 执行数据采集
    print("\n2. 执行数据采集...")
    result = collector.get_gamedata()
    print(f"{'✓' if result else '✗'} 数据采集 {'成功' if result else '失败'}")
    
    # 3. 统计数据库记录
    print("\n3. 统计数据库记录...")
    match_count = localdb.query(BjdcMatch).count()
    tg_odds_count = localdb.query(BjdcTotalGoalOdds).count()
    sc_odds_count = localdb.query(BjdcScoreOdds).count()
    league_count = localdb.query(League).count()
    team_count = localdb.query(Team).count()
    
    print(f"   - 比赛记录：{match_count} 场")
    print(f"   - 总进球赔率：{tg_odds_count} 条")
    print(f"   - 比分赔率：{sc_odds_count} 条")
    print(f"   - 联赛记录：{league_count} 个")
    print(f"   - 球队记录：{team_count} 支")
    
    # 4. 抽样检查数据
    print("\n4. 抽样检查数据...")
    matches = localdb.query(BjdcMatch).limit(3).all()
    for i, m in enumerate(matches, 1):
        print(f"\n   样本 {i}:")
        print(f"      比赛 ID: {m.match_id}")
        print(f"      期数：{m.issue}")
        print(f"      比赛编号：{m.match_num_str}")
        print(f"      联赛 ID: {m.league_id}")
        print(f"      主队 ID: {m.home_team_id}")
        print(f"      客队 ID: {m.away_team_id}")
        
        # 检查关联的总进球赔率
        tg_odds = localdb.query(BjdcTotalGoalOdds).filter_by(match_id=m.match_id).first()
        if tg_odds:
            print(f"      总进球赔率：✓ 已保存")
            print(f"         - 0 球：{tg_odds.goal_0}")
            print(f"         - 1 球：{tg_odds.goal_1}")
            print(f"         - 2 球：{tg_odds.goal_2}")
            print(f"         - 3 球：{tg_odds.goal_3}")
        else:
            print(f"      总进球赔率：✗ 未保存")
        
        # 检查关联的比分赔率
        sc_odds = localdb.query(BjdcScoreOdds).filter_by(match_id=m.match_id).first()
        if sc_odds:
            print(f"      比分赔率：✓ 已保存")
            print(f"         - 1:0: {sc_odds.score_1_0}")
            print(f"         - 2:0: {sc_odds.score_2_0}")
            print(f"         - 2:1: {sc_odds.score_2_1}")
        else:
            print(f"      比分赔率：✗ 未保存")
    
    # 5. 检查联赛处理
    print("\n5. 检查联赛处理...")
    leagues = localdb.query(League).order_by(League.id.desc()).limit(5).all()
    for lg in leagues:
        print(f"   - {lg.league_name} (ID: {lg.league_id}, 简称：{lg.league_name_abbr})")
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    success = result and match_count > 0 and (tg_odds_count > 0 or sc_odds_count > 0)
    if success:
        print("✓ 所有测试通过！")
        print(f"  - 数据采集成功")
        print(f"  - 比赛记录入库：{match_count} 场")
        print(f"  - 赔率数据入库：{tg_odds_count + sc_odds_count} 条")
    else:
        print("✗ 测试失败")
        print(f"  - 采集结果：{'成功' if result else '失败'}")
        print(f"  - 比赛记录：{match_count} 场")
        print(f"  - 赔率记录：{tg_odds_count + sc_odds_count} 条")
    
    return success

if __name__ == '__main__':
    try:
        success = test_bjdc_collector()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
