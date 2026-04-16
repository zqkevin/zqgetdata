# -*- coding: utf-8 -*-
"""
诊断赛果匹配问题
检查 API 返回的赛果与数据库中待匹配比赛的队名是否一致
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import localdb, BjdcMatch
from app.common.req_sporttery_api import SportteryAPI

def diagnose_bjdc_result_match():
    """诊断北京单场赛果匹配问题"""
    
    print("=" * 80)
    print("北京单场赛果匹配诊断")
    print("=" * 80)
    
    # 1. 获取待匹配的比赛
    cutoff_time = datetime.now() - timedelta(hours=4)
    pending_matches = localdb.query(BjdcMatch).filter(
        BjdcMatch.status == 0,
        BjdcMatch.match_time < cutoff_time
    ).all()
    
    print(f"\n📊 待匹配比赛数: {len(pending_matches)}")
    
    if not pending_matches:
        print("✅ 没有待匹配的比赛")
        return
    
    # 显示前 5 场待匹配比赛
    print("\n📋 前 5 场待匹配比赛:")
    for i, match in enumerate(pending_matches[:5], 1):
        home_name = match.home_team.team_full_name if match.home_team else '未知'
        away_name = match.away_team.team_full_name if match.away_team else '未知'
        match_date = match.match_time.strftime('%Y-%m-%d') if match.match_time else '未知'
        print(f"  {i}. [{match_date}] {home_name} vs {away_name} (ID: {match.match_id})")
    
    # 2. 获取 API 返回的赛果
    api = SportteryAPI()
    
    # 统计时间范围
    match_dates = [m.match_time.date() for m in pending_matches if m.match_time]
    if not match_dates:
        print("\n❌ 无法提取比赛日期")
        return
    
    min_date = min(match_dates)
    max_date = max(match_dates)
    
    print(f"\n📅 赛果时间范围: {min_date} 到 {max_date}")
    
    results = api.get_football_match_result(
        match_begin_date=min_date.strftime('%Y-%m-%d'),
        match_end_date=max_date.strftime('%Y-%m-%d')
    )
    
    print(f"📊 API 返回赛果数: {len(results)}")
    
    if not results:
        print("\n❌ API 未返回任何赛果")
        return
    
    # 显示前 5 条 API 赛果
    print("\n📋 前 5 条 API 返回的赛果:")
    for i, result in enumerate(results[:5], 1):
        home_team = result.get('allHomeTeam') or result.get('homeTeam', '未知')
        away_team = result.get('allAwayTeam') or result.get('awayTeam', '未知')
        match_date = result.get('matchDate', '未知')
        home_score = result.get('homeScore', 'N/A')
        away_score = result.get('awayScore', 'N/A')
        print(f"  {i}. [{match_date}] {home_team} vs {away_team} ({home_score}-{away_score})")
    
    # 3. 构建匹配键进行对比
    print("\n" + "=" * 80)
    print("🔍 匹配分析")
    print("=" * 80)
    
    # 构建 API 赛果索引
    api_map = {}
    for result in results:
        home_team = result.get('allHomeTeam') or result.get('homeTeam', '')
        away_team = result.get('allAwayTeam') or result.get('awayTeam', '')
        match_date = result.get('matchDate', '')
        
        if home_team and away_team and match_date:
            key = (match_date, home_team, away_team)
            api_map[key] = result
    
    print(f"\nAPI 赛果索引数: {len(api_map)}")
    
    # 检查每场待匹配比赛
    matched_count = 0
    unmatched_details = []
    
    for match in pending_matches[:10]:  # 只检查前 10 场
        home_name = match.home_team.team_full_name if match.home_team else ''
        away_name = match.away_team.team_full_name if match.away_team else ''
        match_date_str = match.match_time.strftime('%Y-%m-%d') if match.match_time else ''
        
        if not all([home_name, away_name, match_date_str]):
            continue
        
        # 尝试匹配
        api_result = api_map.get((match_date_str, home_name, away_name))
        
        if not api_result:
            # 尝试反向匹配
            api_result = api_map.get((match_date_str, away_name, home_name))
        
        if api_result:
            matched_count += 1
            print(f"\n✅ 匹配成功: {home_name} vs {away_name} ({match_date_str})")
        else:
            unmatched_details.append({
                'match_id': match.match_id,
                'date': match_date_str,
                'home': home_name,
                'away': away_name
            })
    
    print(f"\n前 10 场中匹配成功: {matched_count}/10")
    
    # 4. 详细分析未匹配的原因
    if unmatched_details:
        print("\n" + "=" * 80)
        print("❌ 未匹配比赛详情（前 5 场）:")
        print("=" * 80)
        
        for detail in unmatched_details[:5]:
            print(f"\n比赛 ID: {detail['match_id']}")
            print(f"  日期: {detail['date']}")
            print(f"  主队: {detail['home']}")
            print(f"  客队: {detail['away']}")
            
            # 检查 API 中是否有相同日期的比赛
            same_date_api = [(k, v) for k, v in api_map.items() if k[0] == detail['date']]
            if same_date_api:
                print(f"  📌 API 中同一日期的比赛 ({len(same_date_api)} 场):")
                for (date, api_home, api_away), result in same_date_api[:3]:
                    print(f"     - {api_home} vs {api_away}")
                    
                    # 检查队名相似度
                    if detail['home'] in api_home or api_home in detail['home']:
                        print(f"       ⚠️ 主队名称相似但不完全匹配")
                    if detail['away'] in api_away or api_away in detail['away']:
                        print(f"       ⚠️ 客队名称相似但不完全匹配")
            else:
                print(f"  ❌ API 中没有该日期的比赛")
    
    # 5. 检查队名差异示例
    print("\n" + "=" * 80)
    print("🔎 队名对比示例")
    print("=" * 80)
    
    if pending_matches and results:
        # 找一个未匹配的作为示例
        sample_match = pending_matches[0]
        sample_home = sample_match.home_team.team_full_name if sample_match.home_team else ''
        sample_away = sample_match.away_team.team_full_name if sample_match.away_team else ''
        sample_date = sample_match.match_time.strftime('%Y-%m-%d') if sample_match.match_time else ''
        
        print(f"\n数据库中的队名:")
        print(f"  主队: '{sample_home}'")
        print(f"  客队: '{sample_away}'")
        print(f"  日期: {sample_date}")
        
        # 查找 API 中同一日期的所有比赛
        api_same_date = [r for r in results if r.get('matchDate') == sample_date]
        if api_same_date:
            print(f"\nAPI 中同一日期的队名 (共 {len(api_same_date)} 场):")
            for r in api_same_date[:5]:
                api_home = r.get('allHomeTeam') or r.get('homeTeam', '')
                api_away = r.get('allAwayTeam') or r.get('awayTeam', '')
                print(f"  - '{api_home}' vs '{api_away}'")
                
                # 计算相似度
                if sample_home and api_home:
                    if sample_home == api_home:
                        print(f"    ✅ 主队名称完全匹配")
                    elif sample_home in api_home or api_home in sample_home:
                        print(f"    ⚠️ 主队名称部分匹配 (包含关系)")
                    else:
                        print(f"    ❌ 主队名称完全不同")
    
    print("\n" + "=" * 80)
    print("💡 建议:")
    print("=" * 80)
    print("1. 如果队名完全不同，需要建立队名映射表")
    print("2. 如果队名相似但不完全匹配，需要改进模糊匹配逻辑")
    print("3. 如果 API 中没有对应日期的比赛，可能是数据源问题")
    print("=" * 80)

if __name__ == '__main__':
    try:
        diagnose_bjdc_result_match()
    except Exception as e:
        print(f"\n❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()
