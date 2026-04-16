# -*- coding: utf-8 -*-
"""
检查 API 返回的赛果数据结构
查看是否有系统标识字段
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.common.req_sporttery_api import SportteryAPI
import json

def check_api_structure():
    """检查 API 返回的数据结构"""
    
    print("=" * 80)
    print("检查 API 返回的赛果数据结构")
    print("=" * 80)
    
    api = SportteryAPI()
    
    # 获取今天的赛果
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n📅 查询日期范围: {yesterday} 到 {today}")
    
    results = api.get_football_match_result(
        match_begin_date=yesterday,
        match_end_date=today
    )
    
    print(f"📊 API 返回赛果数: {len(results)}")
    
    if not results:
        print("\n❌ API 未返回任何赛果")
        return
    
    # 显示第一条完整数据
    print("\n" + "=" * 80)
    print("📋 第一条赛果的完整数据结构:")
    print("=" * 80)
    print(json.dumps(results[0], ensure_ascii=False, indent=2))
    
    # 检查所有可能的标识字段
    print("\n" + "=" * 80)
    print("🔍 检查可能的系统标识字段:")
    print("=" * 80)
    
    identifier_fields = [
        'matchId', 'matchID', 'id',
        'lotteryType', 'lottery_type', 'gameType', 'game_type',
        'systemType', 'system_type', 'source', 'platform',
        'matchNum', 'match_num', 'serialNumber', 'serial_number'
    ]
    
    for field in identifier_fields:
        if field in results[0]:
            print(f"  ✅ {field}: {results[0][field]}")
    
    # 列出所有字段
    print("\n" + "=" * 80)
    print("📝 所有可用字段:")
    print("=" * 80)
    all_fields = sorted(results[0].keys())
    for i, field in enumerate(all_fields, 1):
        value = results[0][field]
        # 截断过长的值
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        print(f"  {i:2d}. {field:30s} = {value}")
    
    # 检查多条数据的 matchId 范围
    print("\n" + "=" * 80)
    print("📊 MatchId 范围分析:")
    print("=" * 80)
    
    match_ids = [r.get('matchId') or r.get('matchID') for r in results if r.get('matchId') or r.get('matchID')]
    if match_ids:
        print(f"  最小 ID: {min(match_ids)}")
        print(f"  最大 ID: {max(match_ids)}")
        print(f"  平均 ID: {sum(match_ids) // len(match_ids)}")
        
        # 判断是哪个系统
        avg_id = sum(match_ids) // len(match_ids)
        if avg_id > 2000000:
            print(f"\n  ⚠️  这看起来是 tczq（体彩足球）系统的 ID（通常 > 2000000）")
        elif avg_id > 1000000:
            print(f"\n  ⚠️  这可能是 bjdc（北京单场）系统的 ID（通常 1000000-2000000）")
        else:
            print(f"\n  ❓ 无法判断系统类型")
    
    # 对比数据库中的 bjdc 比赛 ID
    from app.database import localdb, BjdcMatch
    
    pending_matches = localdb.query(BjdcMatch).filter(
        BjdcMatch.status == 0,
        BjdcMatch.match_time < datetime.now() - timedelta(hours=4)
    ).all()
    
    if pending_matches:
        bjdc_ids = [m.match_id for m in pending_matches[:10]]
        print(f"\n  📊 数据库中前 10 场 bjdc 比赛的 match_id:")
        for mid in bjdc_ids:
            print(f"     - {mid}")
        
        avg_bjdc_id = sum(bjdc_ids) // len(bjdc_ids)
        print(f"\n  bjdc 平均 ID: {avg_bjdc_id}")
        
        if match_ids:
            avg_api_id = sum(match_ids) // len(match_ids)
            diff = abs(avg_api_id - avg_bjdc_id)
            print(f"  API 平均 ID: {avg_api_id}")
            print(f"  ID 差异: {diff}")
            
            if diff > 100000:
                print(f"\n  ❌ ID 差异过大，API 返回的不是 bjdc 数据！")
            else:
                print(f"\n  ✅ ID 相近，可能是同一系统")

if __name__ == '__main__':
    try:
        check_api_structure()
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
