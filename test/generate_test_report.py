# -*- coding: utf-8 -*-
"""
爬虫系统综合测试报告
生成时间：2026-04-01
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localdb, DigitalLotteryDraw, DigitalLotteryPrize, FootballMatch, MatchResult, SpfOdds, TcbkMatch, TcbkResult, TcbkSpf

def print_section(title):
    """打印章节标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_digital_lottery():
    """检查数字彩数据"""
    print_section("🎰 数字彩数据验证")
    
    # 查询开奖记录
    draws = localdb.query(DigitalLotteryDraw).all()
    prizes = localdb.query(DigitalLotteryPrize).all()
    
    print(f"\n✅ 开奖记录总数：{len(draws)}条")
    
    # 按彩种统计
    lottery_types = {}
    for draw in draws:
        if draw.lottery_name not in lottery_types:
            lottery_types[draw.lottery_name] = []
        lottery_types[draw.lottery_name].append(draw)
    
    print("\n📊 各彩种数据统计:")
    for name, draws_list in lottery_types.items():
        print(f"  - {name}: {len(draws_list)}期")
        # 显示最新一期
        latest = draws_list[0]
        print(f"    最新：第{latest.draw_num}期 结果：{latest.draw_result}")
    
    print(f"\n✅ 奖级记录总数：{len(prizes)}条")
    
    # 验证数据完整性
    missing_draw_num = sum(1 for d in draws if not d.draw_num)
    missing_result = sum(1 for d in draws if not d.draw_result)
    
    if missing_draw_num > 0 or missing_result > 0:
        print(f"\n⚠️  数据完整性问题:")
        if missing_draw_num:
            print(f"   - {missing_draw_num}条记录缺少期号")
        if missing_result:
            print(f"   - {missing_result}条记录缺少开奖结果")
    else:
        print("\n✅ 所有记录数据完整")
    
    return len(draws) > 0

def check_football():
    """检查足球数据"""
    print_section("⚽ 足球比赛数据验证")
    
    matches = localdb.query(FootballMatch).all()
    results = localdb.query(MatchResult).all()
    odds = localdb.query(SpfOdds).all()
    
    print(f"\n✅ 比赛记录总数：{len(matches)}条")
    print(f"✅ 赛果记录总数：{len(results)}条")
    print(f"✅ 胜平负赔率记录：{len(odds)}条")
    
    # 检查球队 ID
    missing_home_team = sum(1 for m in matches if not m.home_team_id)
    missing_away_team = sum(1 for m in matches if not m.away_team_id)
    
    if missing_home_team > 0 or missing_away_team > 0:
        print(f"\n⚠️  球队信息不完整:")
        if missing_home_team:
            print(f"   - {missing_home_team}场比赛缺少主队 ID")
        if missing_away_team:
            print(f"   - {missing_away_team}场比赛缺少客队 ID")
    else:
        print("\n✅ 所有比赛球队信息完整")
    
    # 显示部分比赛
    if matches:
        print("\n📋 部分比赛列表:")
        for match in matches[:5]:
            print(f"  {match.match_num_str}: 球队{match.home_team_id} vs 球队{match.away_team_id}")
    
    return len(matches) > 0

def check_basketball():
    """检查篮球数据"""
    print_section("🏀 篮球比赛数据验证")
    
    matches = localdb.query(TcbkMatch).all()
    results = localdb.query(TcbkResult).all()
    spf_odds = localdb.query(TcbkSpf).all()
    
    print(f"\n✅ 比赛记录总数：{len(matches)}条")
    print(f"✅ 赛果记录总数：{len(results)}条")
    print(f"✅ 胜分差赔率记录：{len(spf_odds)}条")
    
    # 检查球队信息
    missing_home_code = sum(1 for m in matches if not m.home_team_code)
    missing_away_code = sum(1 for m in matches if not m.away_team_code)
    
    if missing_home_code > 0 or missing_away_code > 0:
        print(f"\n⚠️  球队信息不完整:")
        if missing_home_code:
            print(f"   - {missing_home_code}场比赛缺少主队代码")
        if missing_away_code:
            print(f"   - {missing_away_code}场比赛缺少客队代码")
    else:
        print("\n✅ 所有比赛球队信息完整")
    
    # 显示部分比赛
    if matches:
        print("\n📋 部分比赛列表:")
        for match in matches[:5]:
            home = match.home_team_code or "未知"
            away = match.away_team_code or "未知"
            print(f"  {match.match_num_str}: {home} vs {away}")
    
    return len(matches) > 0

def check_bjdc():
    """检查北京单场数据"""
    print_section("🏟️ 北京单场数据验证")
    
    print("\n⚠️  北京单场爬虫代码存在，但数据库模型待完善")
    print("   需要进一步修复球队 ID 为 null 的问题")
    return False

def generate_summary():
    """生成测试总结"""
    print_section("📊 测试总结")
    
    results = []
    
    # 数字彩
    lottery_ok = check_digital_lottery()
    results.append(("数字彩爬虫", lottery_ok))
    
    # 足球
    football_ok = check_football()
    results.append(("传统足球爬虫", football_ok))
    
    # 篮球
    basketball_ok = check_basketball()
    results.append(("篮球竞猜爬虫", basketball_ok))
    
    # 北京单场
    bjdc_ok = check_bjdc()
    results.append(("北京单场爬虫", bjdc_ok))
    
    # 总体评估
    print("\n" + "="*70)
    print("  总体评估")
    print("="*70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "⚠️ 待完善"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("  🎉 所有爬虫测试完成，数据基本正常!")
    else:
        print("  ⚠️  部分爬虫存在问题，需要进一步修复")
    print("="*70 + "\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  体育彩票爬虫系统综合测试报告")
    print(f"  测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    generate_summary()
