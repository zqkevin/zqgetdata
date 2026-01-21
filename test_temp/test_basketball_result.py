#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试篮球赛果接口
"""
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from controls.req_sporttery_api import SportteryAPI

def test_basketball_result():
    """
    测试篮球赛果接口
    """
    print("===== 测试篮球赛果接口 =====")
    
    try:
        # 初始化API客户端
        api = SportteryAPI()
        
        # 测试篮球赛果接口 - 使用当前日期
        match_date = "2025-12-27"
        print(f"\n获取{match_date}的篮球赛果...")
        result_data = api.get_basketball_match_result(match_date)
        
        print(f"响应数据结构: {json.dumps(result_data, ensure_ascii=False, indent=2)}")
        
        # 测试篮球比赛计算器接口
        print(f"\n获取篮球比赛计算器信息...")
        calculator_data = api.get_basketball_match_calculator(['hilo'])
        
        print(f"响应数据结构: {json.dumps(calculator_data, ensure_ascii=False, indent=2)}")
        
        # 测试篮球比赛列表接口
        print(f"\n获取篮球比赛列表...")
        match_list = api.get_basketball_match_list()
        
        print(f"比赛列表行数: {len(match_list)}")
        if not match_list.empty:
            print(f"比赛列表前几行: {match_list.head().to_json(orient='records', ensure_ascii=False, indent=2)}")
        
        api.close()
        print("\n测试完成！")
        return True
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_basketball_result()