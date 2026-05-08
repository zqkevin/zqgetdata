import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'get_data'))

from app.common.req_sporttery_api import SportteryAPI
import json
from datetime import datetime, timedelta

print("=" * 100)
print("测试TCBK赛果API数据")
print("=" * 100)

api = SportteryAPI()

# 获取最近7天的赛果
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

print(f"\n1. 获取篮球赛果数据 ({start_date} 到 {end_date})...")
try:
    results = api.get_basketball_match_results(
        match_begin_date=start_date,
        match_end_date=end_date
    )
    
    print(f"   返回类型: {type(results)}")
    print(f"   数据条数: {len(results) if results else 0}")
    
    if results and len(results) > 0:
        print("\n2. 第一条赛果数据的完整结构:")
        first_result = results[0]
        print(json.dumps(first_result, indent=2, ensure_ascii=False, default=str))
        
        # 重点检查关键字段
        print("\n3. 关键字段检查:")
        print(f"   - matchId: {first_result.get('matchId')}")
        print(f"   - allHomeTeam: {first_result.get('allHomeTeam')}")
        print(f"   - allAwayTeam: {first_result.get('allAwayTeam')}")
        print(f"   - homeTeam: {first_result.get('homeTeam')}")
        print(f"   - awayTeam: {first_result.get('awayTeam')}")
        print(f"   - matchDate: {first_result.get('matchDate')}")
        print(f"   - homeScore: {first_result.get('homeScore')}")
        print(f"   - awayScore: {first_result.get('awayScore')}")
        print(f"   - status: {first_result.get('status')} (类型: {type(first_result.get('status'))})")
        print(f"   - resultStatus: {first_result.get('resultStatus')}")
        print(f"   - poolStatus: {first_result.get('poolStatus')}")
        print(f"   - matchResultStatus: {first_result.get('matchResultStatus')}")
        
        # 检查是否有其他可能的ID字段
        print("\n4. 所有包含'Id'或'ID'的字段:")
        for key in first_result.keys():
            if 'id' in key.lower() or 'Id' in key:
                print(f"   - {key}: {first_result.get(key)}")
        
        # 检查所有字段名
        print("\n5. 所有字段名列表:")
        for key in sorted(first_result.keys()):
            value = first_result.get(key)
            if value is not None:
                print(f"   - {key}: {value} (类型: {type(value).__name__})")
            else:
                print(f"   - {key}: None")
                
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
