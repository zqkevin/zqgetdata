# -*- coding: utf-8 -*-
"""
测试API返回的数据结构，特别是赔率部分
"""
import os
import sys
import json

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from app.common.req_sporttery_api import SportteryAPI

def test_api_data():
    """
    测试API返回的数据结构
    """
    api = SportteryAPI()
    
    print("=== 测试API返回的数据结构开始 ===")
    
    try:
        # 获取当前可投注的足球比赛列表
        print("正在获取当前赛事信息...")
        match_data = api.get_football_match_list(pool_codes=["had", "hhad", "ttg", "hafu", "crs"])
        
        if not match_data:
            print("未获取到赛事数据")
            return
        
        # 处理联赛信息
        league_list = match_data.get("league_list", [])
        print(f"\n联赛列表 ({len(league_list)} 个):")
        print("-" * 50)
        for league in league_list[:3]:  # 只显示前3个
            print(json.dumps(league, ensure_ascii=False, indent=2))
        
        # 处理比赛信息
        match_info_list = match_data.get("match_info_list", [])
        print(f"\n比赛信息列表 ({len(match_info_list)} 个日期/时间段):")
        print("-" * 50)
        
        total_matches = 0
        had_hhad_found = False
        for idx, date_match_set in enumerate(match_info_list):
            print(f"\n日期/时间段 {idx+1}:")
            
            # 获取真正的比赛列表
            sub_match_list = date_match_set.get('subMatchList', [])
            total_matches += len(sub_match_list)
            print(f"该集合包含 {len(sub_match_list)} 场比赛")
            
            # 显示前2场比赛的详细信息
            for sub_idx, match in enumerate(sub_match_list[:2]):
                print(f"\n  比赛 {sub_idx+1}:")
                print(json.dumps(match, ensure_ascii=False, indent=2))
                
                # 特别打印赔率部分
                print("\n  赔率部分:")
                for pool_code in ["had", "hhad", "ttg", "hafu", "crs"]:
                    odds = match.get(pool_code, {})
                    print(f"    {pool_code}: {json.dumps(odds, ensure_ascii=False)}")
            
            # 专门查找包含had和hhad数据的比赛
            if not had_hhad_found:
                print("\n--- 专门查找包含had和hhad数据的比赛 ---")
                for match in sub_match_list:
                    had = match.get('had', {})
                    hhad = match.get('hhad', {})
                    if had and had != {} and hhad and hhad != {}:
                        print(f"\n找到包含had和hhad数据的比赛:")
                        print("had数据:", json.dumps(had, ensure_ascii=False))
                        print("hhad数据:", json.dumps(hhad, ensure_ascii=False))
                        had_hhad_found = True
                        break
                if had_hhad_found:
                    break
            
            # 只处理前2个日期/时间段
            if idx >= 1:
                break
        
        print(f"\n总共 {total_matches} 场比赛")
        
    except Exception as e:
        print(f"获取数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试API返回的数据结构结束 ===")

if __name__ == "__main__":
    test_api_data()