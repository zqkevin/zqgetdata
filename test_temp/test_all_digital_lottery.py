#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字彩票API接口测试脚本
用于测试七星彩、排列3、排列5和大乐透的API接口
"""

import requests
import json
import os

# 基本请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.sporttery.cn/',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

def test_digital_lottery_api(param, is_verify=1):
    """
    测试数字彩票API接口
    
    参数:
    param: 格式为"彩票类型代码,期号标识"，支持多个彩种用逗号分隔
    is_verify: 是否需要验证(0或1)
    
    返回:
    response.json(): API响应数据
    """
    url = 'https://webapi.sporttery.cn/gateway/lottery/getDigitalDrawInfoV1.qry'
    params = {
        'param': param,
        'isVerify': is_verify
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def test_history_page_list_api(game_no, province_id=0, is_verify=1, term_limits=13):
    """
    测试历史开奖列表API接口
    
    参数:
    game_no: 彩票游戏编号
    province_id: 省份ID，0表示全国
    is_verify: 是否需要验证(0或1)
    term_limits: 获取的期数限制
    
    返回:
    response.json(): API响应数据
    """
    url = 'https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry'
    params = {
        'gameNo': game_no,
        'provinceId': province_id,
        'isVerify': is_verify,
        'termLimits': term_limits
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def save_response_to_file(data, filename):
    """将API响应数据保存到文件"""
    # 创建输出目录
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存数据到文件
    file_path = os.path.join(output_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"响应数据已保存到: {file_path}")

def analyze_lottery_data(data, lottery_name):
    """分析彩票数据的结构"""
    if not data or 'errorCode' not in data:
        print("无效的响应数据")
        return
    
    print(f"错误码: {data['errorCode']}")
    print(f"错误信息: {data['errorMessage']}")
    
    if data['errorCode'] == '0' and 'value' in data:
        value = data['value']
        
        # 处理同时包含多种彩票数据的情况
        if lottery_name == '排列3和排列5':
            # 检查是否同时包含pls和plw数据
            if 'pls' in value and value['pls'] and 'plw' in value and value['plw']:
                print(f"\n成功获取到排列3和排列5的数据")
                
                # 分析排列3数据
                pls_data = value['pls']
                print(f"\n排列3数据中的键: {list(pls_data.keys())}")
                print(f"\n排列3基本信息:")
                for key in ['lotteryGameName', 'lotteryDrawNum', 'lotteryDrawTime', 'lotteryDrawResult']:
                    if key in pls_data:
                        print(f"  {key}: {pls_data[key]}")
                
                # 分析排列5数据
                plw_data = value['plw']
                print(f"\n排列5数据中的键: {list(plw_data.keys())}")
                print(f"\n排列5基本信息:")
                for key in ['lotteryGameName', 'lotteryDrawNum', 'lotteryDrawTime', 'lotteryDrawResult']:
                    if key in plw_data:
                        print(f"  {key}: {plw_data[key]}")
                
                # 打印排列3期号列表
                if 'termList' in pls_data:
                    print(f"\n排列3期号列表(共{len(pls_data['termList'])}期): {pls_data['termList'][:10]}...")
                
                # 打印排列5期号列表
                if 'termList' in plw_data:
                    print(f"\n排列5期号列表(共{len(plw_data['termList'])}期): {plw_data['termList'][:10]}...")
            else:
                print(f"\n未同时找到排列3和排列5的数据")
                print(f"排列3数据存在: {'pls' in value and value['pls']}")
                print(f"排列5数据存在: {'plw' in value and value['plw']}")
        elif lottery_name == '多个彩种同时获取':
            # 检查并分析所有可能的彩种数据
            lottery_types = {
                'dlt': '大乐透',
                'pls': '排列3',
                'plw': '排列5',
                'qxc': '七星彩'
            }
            
            found_count = 0
            for key, name in lottery_types.items():
                if key in value and value[key]:
                    found_count += 1
                    print(f"\n{name}数据中的键: {list(value[key].keys())}")
                    print(f"\n{name}基本信息:")
                    for info_key in ['lotteryGameName', 'lotteryDrawNum', 'lotteryDrawTime', 'lotteryDrawResult']:
                        if info_key in value[key]:
                            print(f"  {info_key}: {value[key][info_key]}")
            
            print(f"\n共成功获取到{found_count}个彩种的数据")
        else:
            # 找出对应彩票类型的数据键
            # 大乐透对应'dlt'，排列3对应'pls'，排列5对应'plw'，七星彩对应'qxc'
            lottery_keys = {
                '大乐透': 'dlt',
                '排列3': 'pls',
                '排列5': 'plw',
                '七星彩': 'qxc'
            }
            
            lottery_key = lottery_keys.get(lottery_name)
            
            if lottery_key in value and value[lottery_key]:
                lottery_data = value[lottery_key]
                print(f"\n{lottery_name}数据中的键: {list(lottery_data.keys())}")
                
                # 打印基本信息
                print(f"\n{lottery_name}基本信息:")
                for key in ['lotteryGameName', 'lotteryDrawNum', 'lotteryDrawTime', 'lotteryDrawResult']:
                    if key in lottery_data:
                        print(f"  {key}: {lottery_data[key]}")
                
                # 打印奖池信息
                if 'poolInfo' in lottery_data:
                    print(f"\n奖池信息:")
                    for key, val in lottery_data['poolInfo'].items():
                        print(f"  {key}: {val}")
                
                # 打印奖级信息
                if 'awardList' in lottery_data:
                    print(f"\n奖级信息(共{len(lottery_data['awardList'])}个奖级):")
                    for award in lottery_data['awardList']:
                        print(f"  {award.get('prizeLevel', '未知奖级')}: 注数={award.get('stakeCount', '0')}, 奖金总额={award.get('totalPrizeamount', '0')}")
                
                # 打印期号列表
                if 'termList' in lottery_data:
                    print(f"\n期号列表(共{len(lottery_data['termList'])}期): {lottery_data['termList'][:10]}...")
            else:
                print(f"\n未找到{lottery_name}的数据")

def analyze_history_page_list_data(data, game_no):
    """分析历史开奖列表数据结构"""
    if not data or 'errorCode' not in data:
        print("无效的响应数据")
        return
    
    print(f"错误码: {data['errorCode']}")
    print(f"错误信息: {data['errorMessage']}")
    
    if data['errorCode'] == '0' and 'value' in data:
        value = data['value']
        print(f"\n历史开奖列表数据中的键: {list(value.keys())}")
        
        # 打印基本信息
        for key in ['gameName', 'historyList', 'nextAwardList']:
            if key in value:
                if key == 'historyList':
                    print(f"\nhistoryList长度: {len(value[key])}")
                    if len(value[key]) > 0:
                        print(f"\n最近一期开奖信息: {json.dumps(value[key][0], ensure_ascii=False)}")
                else:
                    print(f"\n{key}: {value[key]}")
        
        print(f"\ngameNo={game_no} 的数据解析完成")

def run_tests():
    """运行所有测试用例"""
    print("=" * 60)
    print("数字彩票API接口测试")
    print("=" * 60)
    
    # 彩票类型测试列表
    lottery_types = [
        ("大乐透", "85,0"),
        ("排列3", "35,0"),
        ("排列5", "350133,0"),
        ("七星彩", "04,0"),
        ("排列3和排列5", "35,0")  # 测试同时获取排列3和排列5
    ]
    
    for i, (lottery_name, param) in enumerate(lottery_types, 1):
        print(f"\n测试用例{i}: {lottery_name} 最近一期")
        print("-" * 40)
        data = test_digital_lottery_api(param)
        if data:
            save_response_to_file(data, f"{lottery_name.replace(' ', '_')}_latest.json")
            analyze_lottery_data(data, lottery_name)
    
    # 测试同时获取四个彩种 (35,04,85,350133)
    print(f"\n测试用例: 同时获取四个彩种(排列3,七星彩,大乐透,排列5)")
    print("-" * 40)
    
    # 四个彩种的参数列表
    four_lotteries = [
        ("排列3", "35,0"),
        ("七星彩", "04,0"),
        ("大乐透", "85,0"),
        ("排列5", "350133,0")
    ]
    
    # 分别请求每个彩种的数据
    all_results = {}
    for lottery_name, param in four_lotteries:
        data = test_digital_lottery_api(param)
        if data:
            all_results[lottery_name] = data
            print(f"  ✓ 成功获取{lottery_name}数据")
        else:
            print(f"  ✗ 无法获取{lottery_name}数据")
    
    # 保存合并结果
    if all_results:
        save_response_to_file(all_results, "四个彩种同时获取_latest.json")
        
        # 分析每个彩种的数据
        print("\n" + "=" * 40)
        print("四个彩种数据详细信息:")
        print("=" * 40)
        
        for lottery_name, data in all_results.items():
            print(f"\n{lottery_name}:")
            print("-" * 20)
            analyze_lottery_data(data, lottery_name)
    
    # 测试historyPageList API
    print("\n" + "=" * 60)
    print("历史开奖列表API测试")
    print("=" * 60)
    
    # 测试不同gameNo的情况
    game_nos_to_test = ['04', '35', '85', '350133']
    for game_no in game_nos_to_test:
        print(f"\n测试用例: gameNo={game_no}")
        print("-" * 40)
        data = test_history_page_list_api(game_no)
        if data:
            save_response_to_file(data, f"history_gameNo_{game_no}.json")
            analyze_history_page_list_data(data, game_no)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()