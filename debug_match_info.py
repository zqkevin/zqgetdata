# -*- coding: utf-8 -*-
"""
调试脚本，用于检查足球比赛信息API返回的数据结构
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controls.req_sporttery_api import SportteryAPI

def debug_match_info():
    """
    调试足球比赛信息API返回的数据结构
    """
    try:
        api = SportteryAPI()
        
        # 获取足球比赛列表
        print("正在调用API获取比赛列表...")
        match_data = api.get_football_match_list(pool_codes=["had", "hhad", "ttg", "hafu", "crs"])
        
        # 打印返回数据的整体结构
        print(f"\nAPI返回数据类型: {type(match_data)}")
        print(f"API返回数据键: {list(match_data.keys())}")
        
        # 打印联赛列表信息
        league_list = match_data.get("league_list", [])
        print(f"\n联赛列表数量: {len(league_list)}")
        for league in league_list:
            print(f"  - {league.get('leagueId')}: {league.get('leagueName')} ({league.get('leagueNameAbbr')})")
        
        # 打印比赛列表信息
        match_info_list = match_data.get("match_info_list", [])
        print(f"\n比赛列表数量: {len(match_info_list)}")
        
        # 如果有比赛，打印每场比赛的基本信息和完整字段列表
        if match_info_list:
            print(f"\n每场比赛的基本字段:")
            for idx, match in enumerate(match_info_list):
                print(f"\n第 {idx+1} 场比赛字段列表:")
                print(f"所有字段: {list(match.keys())}")
                print(f"\n关键字段值:")
                print(f"businessDate: {match.get('businessDate')}")
                print(f"weekday: {match.get('weekday')}")
                print(f"matchCount: {match.get('matchCount')}")
                print(f"matchNumDate: {match.get('matchNumDate')}")
                
                # 查看subMatchList字段
                sub_match_list = match.get('subMatchList', [])
                print(f"\nsubMatchList数量: {len(sub_match_list)}")
                
                for sub_idx, sub_match in enumerate(sub_match_list):
                    print(f"\n  子比赛 {sub_idx+1} 字段列表:")
                    print(f"  所有字段: {list(sub_match.keys())}")
                    print(f"  \n  关键字段值:")
                    print(f"  matchId: {sub_match.get('matchId')}")
                    print(f"  matchNum: {sub_match.get('matchNum')}")
                    print(f"  lineId: {sub_match.get('lineId')}")
                    print(f"  matchDate: {sub_match.get('matchDate')}")
                    print(f"  matchTime: {sub_match.get('matchTime')}")
                    print(f"  leagueId: {sub_match.get('leagueId')}")
                    print(f"  homeTeamId: {sub_match.get('homeTeamId')}")
                    print(f"  awayTeamId: {sub_match.get('awayTeamId')}")
                
            # 保存原始数据到文件以便进一步分析
            with open(os.path.join(os.path.dirname(__file__), "temp", "match_data_debug.json"), "w", encoding="utf-8") as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            print(f"\n原始数据已保存到: temp/match_data_debug.json")
        else:
            print("\n没有比赛数据")
            
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 创建temp文件夹
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    debug_match_info()