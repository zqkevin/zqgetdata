# -*- coding: utf-8 -*-
"""
测试篮球API返回的实际数据结构
"""
import sys
import os
import json

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from app.common.req_sporttery_api import SportteryAPI

print("\n" + "="*70)
print(" " * 20 + "测试篮球API返回数据结构")
print("="*70)

try:
    api = SportteryAPI()
    
    print("\n【测试】获取篮球比赛计算器数据")
    print("-"*70)
    
    # 调用API
    result = api.get_basketball_match_calculator(['hilo', 'spf', 'rfsf', 'sfc'])
    
    print(f"\n返回数据类型: {type(result)}")
    print(f"返回数据的键: {result.keys() if isinstance(result, dict) else 'N/A'}")
    
    # 保存完整数据到文件
    output_file = 'basketball_api_response.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 完整数据已保存到: {output_file}")
    
    # 显示关键信息
    if isinstance(result, dict):
        if 'matchInfoList' in result:
            match_list = result['matchInfoList']
            print(f"\nmatchInfoList 长度: {len(match_list)}")
            
            if match_list:
                first_match = match_list[0]
                print(f"\n第一场比赛的关键字段:")
                for key in ['matchId', 'subMatchList']:
                    if key in first_match:
                        value = first_match[key]
                        if key == 'subMatchList' and isinstance(value, list) and value:
                            print(f"  {key}: [{len(value)} items]")
                            # 显示subMatchList的第一个元素的部分字段
                            sub_first = value[0]
                            print(f"    subMatchList[0] 的键: {list(sub_first.keys())[:15]}")
                        else:
                            print(f"  {key}: {value}")
        
        # 检查是否有其他重要字段
        important_keys = ['businessDate', 'matchCount', 'weekday']
        for key in important_keys:
            if key in result:
                print(f"{key}: {result[key]}")
    
    print("\n" + "="*70)
    print("测试完成！请查看 basketball_api_response.json 了解完整结构")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n✗ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*70 + "\n")
