import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'get_data'))

from app.crawler.jcbk import JcbkDataCollector
import json

print("=" * 100)
print("测试TCBK API数据返回")
print("=" * 100)

collector = JcbkDataCollector()

# 获取比赛列表
print("\n1. 获取篮球比赛列表...")
try:
    match_list = collector.api.get_basketball_match_list()
    print(f"   返回类型: {type(match_list)}")
    print(f"   数据条数: {len(match_list)}")
    
    if len(match_list) > 0:
        print("\n2. 第一条数据的完整结构:")
        first_row = match_list.iloc[0]
        print(json.dumps(first_row.to_dict(), indent=2, ensure_ascii=False, default=str))
        
        # 检查subMatchList
        if 'subMatchList' in first_row:
            sub_matches = first_row['subMatchList']
            print(f"\n3. subMatchList包含 {len(sub_matches)} 场比赛")
            if len(sub_matches) > 0:
                print("\n4. 第一场比赛的详细信息:")
                first_match = sub_matches[0]
                print(json.dumps(first_match, indent=2, ensure_ascii=False, default=str))
                
                # 重点检查关键字段
                print("\n5. 关键字段检查:")
                print(f"   - matchId: {first_match.get('matchId')}")
                print(f"   - matchTime: {first_match.get('matchTime')} (类型: {type(first_match.get('matchTime'))})")
                print(f"   - businessDate: {first_match.get('businessDate')}")
                print(f"   - matchDate: {first_match.get('matchDate')}")
                print(f"   - matchStatus: {first_match.get('matchStatus')} (类型: {type(first_match.get('matchStatus'))})")
                print(f"   - poolStatus: {first_match.get('poolStatus')}")
                print(f"   - sellStatus: {first_match.get('sellStatus')}")
                
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
