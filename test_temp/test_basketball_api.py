#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试篮球API接口的返回数据
"""
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from controls.req_sporttery_api import SportteryAPI
    
    print("=== 测试篮球API接口 ===")
    
    # 初始化API客户端
    api = SportteryAPI()
    
    # 测试篮球比赛列表接口
    print("\n1. 测试篮球比赛列表接口:")
    try:
        match_list = api.get_basketball_match_list()
        print(f"返回类型: {type(match_list)}")
        print(f"返回数据数量: {len(match_list)}")
        if not match_list.empty:
            print("前5条数据:")
            print(match_list.head())
        else:
            print("返回的DataFrame为空")
    except Exception as e:
        print(f"✗ 获取篮球比赛列表失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试篮球比赛计算器接口
    print("\n2. 测试篮球比赛计算器接口:")
    try:
        calculator_data = api.get_basketball_match_calculator(['hilo', 'spf', 'rfsf', 'sfc'])
        print(f"返回类型: {type(calculator_data)}")
        print(f"包含的键: {list(calculator_data.keys())}")
        
        if 'matchInfoList' in calculator_data:
            print(f"matchInfoList数量: {len(calculator_data['matchInfoList'])}")
            if calculator_data['matchInfoList']:
                print("第一条比赛信息:")
                print(json.dumps(calculator_data['matchInfoList'][0], ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"✗ 获取篮球比赛计算器数据失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试篮球比赛赛果接口
    print("\n3. 测试篮球比赛赛果接口:")
    try:
        # 尝试获取昨天的数据（因为今天可能没有比赛结束）
        import datetime
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        result_data = api.get_basketball_match_result(yesterday)
        print(f"获取日期: {yesterday}")
        print(f"返回类型: {type(result_data)}")
        print(f"包含的键: {list(result_data.keys())}")
        
        if 'matchResultList' in result_data:
            print(f"matchResultList数量: {len(result_data['matchResultList'])}")
            if result_data['matchResultList']:
                print("第一条赛果信息:")
                print(json.dumps(result_data['matchResultList'][0], ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"✗ 获取篮球比赛赛果失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")
    
except Exception as e:
    print(f"✗ 测试脚本执行失败: {e}")
    import traceback
    traceback.print_exc()