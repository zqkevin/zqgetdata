# -*- coding: utf-8 -*-
"""
检查TCZQ API返回的比赛数据结构
"""
import sys
import os
import json

# 添加项目根目录到 Python 路径
project_root = os.path.join(os.path.dirname(__file__), 'get_data')
sys.path.append(project_root)

from app.common.req_sporttery_api import SportteryAPI

def check_tczq_api_structure():
    """检查TCZQ API返回的数据结构"""
    api = SportteryAPI()
    
    print("=" * 80)
    print("检查TCZQ API返回的比赛数据结构")
    print("=" * 80)
    
    # 获取比赛列表
    data = api.get_football_match_list()
    
    if not data or not data.get('match_info_list'):
        print("❌ 无法获取比赛数据")
        return
    
    match_info_list = data['match_info_list']
    print(f"\n✅ 成功获取 {len(match_info_list)} 个日期组的比赛")
    
    # 提取所有子比赛
    all_matches = []
    for date_group in match_info_list:
        sub_matches = date_group.get('subMatchList', [])
        all_matches.extend(sub_matches)
    
    print(f"✅ 共获取 {len(all_matches)} 场比赛")
    
    if not all_matches:
        print("❌ 没有比赛数据")
        return
    
    # 检查第一场比赛的完整结构
    first_match = all_matches[0]
    print("\n【第一场比赛的完整数据结构】")
    print("-" * 80)
    print(json.dumps(first_match, ensure_ascii=False, indent=2))
    
    # 检查是否有状态相关字段
    print("\n【状态相关字段检查】")
    print("-" * 80)
    status_fields = [key for key in first_match.keys() if 'status' in key.lower() or 'Status' in key]
    if status_fields:
        print(f"找到状态字段: {status_fields}")
        for field in status_fields:
            print(f"  {field}: {first_match[field]}")
    else:
        print("❌ 未找到任何状态相关字段")
    
    # 检查所有比赛的字段一致性
    print("\n【所有比赛的字段统计】")
    print("-" * 80)
    all_keys = set()
    for match in all_matches[:10]:  # 只检查前10场
        all_keys.update(match.keys())
    
    print(f"前10场比赛中出现的字段总数: {len(all_keys)}")
    print(f"字段列表: {sorted(all_keys)}")
    
    # 保存完整数据到文件供分析
    output_file = os.path.join(os.path.dirname(__file__), 'tczq_api_sample.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_matches': len(all_matches),
            'sample_match': first_match,
            'all_field_names': sorted(all_keys)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完整数据已保存到: {output_file}")

if __name__ == '__main__':
    check_tczq_api_structure()
