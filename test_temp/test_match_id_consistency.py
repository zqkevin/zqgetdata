#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试篮球比赛ID的一致性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controls.req_sporttery_api import SportteryAPI
from database.tcbk_models import TcbkMatch
from database.database import localdb


def test_match_id_consistency():
    """
    测试比赛列表和计算器接口返回的matchId是否一致
    """
    print("正在测试篮球比赛ID的一致性...")
    
    # 初始化API
    api = SportteryAPI()
    
    # 1. 获取比赛列表
    print("\n1. 获取比赛列表...")
    match_list_df = api.get_basketball_match_list()
    if match_list_df.empty:
        print("   比赛列表为空")
    else:
        print(f"   比赛列表共有{len(match_list_df)}条记录")
        print("   比赛ID列表:")
        for idx, row in match_list_df.iterrows():
            print(f"   - matchId: {row['matchId']}, 类型: {type(row['matchId'])}")
    
    # 2. 获取计算器数据
    print("\n2. 获取计算器数据...")
    calculator_data = api.get_basketball_match_calculator(['hilo', 'spf', 'rfsf', 'sfc'])
    match_info_list = calculator_data.get('matchInfoList', [])
    if not match_info_list:
        print("   计算器数据为空")
    else:
        print(f"   计算器数据共有{len(match_info_list)}条记录")
        
        # 检查subMatchList
        print("   计算器数据中的比赛ID:")
        for match_info in match_info_list:
            sub_match_list = match_info.get('subMatchList', [])
            if sub_match_list:
                for sub_match in sub_match_list:
                    match_id = sub_match.get('matchId')
                    if match_id:
                        print(f"   - matchId: {match_id}, 类型: {type(match_id)}")
            else:
                # 兼容原来的格式
                match_id = match_info.get('matchId')
                if match_id:
                    print(f"   - matchId: {match_id}, 类型: {type(match_id)}")
    
    # 3. 检查数据库中的记录
    print("\n3. 检查数据库中的记录...")
    db_matches = localdb.query(TcbkMatch).all()
    if not db_matches:
        print("   数据库中没有篮球比赛记录")
    else:
        print(f"   数据库中共有{len(db_matches)}条篮球比赛记录")
        print("   数据库中的比赛ID:")
        for match in db_matches:
            print(f"   - matchId: {match.match_id}, 类型: {type(match.match_id)}")
    
    print("\n测试完成!")


if __name__ == "__main__":
    test_match_id_consistency()