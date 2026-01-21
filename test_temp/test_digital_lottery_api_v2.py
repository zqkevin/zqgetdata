#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字彩票API接口测试脚本(版本2)
用于验证getDigitalDrawInfoV1.qry接口的参数要求和返回数据结构
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
    param: 格式为"彩票类型代码,期号标识"
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

def analyze_lottery_data(data):
    """分析彩票数据的结构"""
    if not data or 'errorCode' not in data:
        print("无效的响应数据")
        return
    
    print(f"错误码: {data['errorCode']}")
    print(f"错误信息: {data['errorMessage']}")
    
    if data['errorCode'] == '0' and 'value' in data:
        value = data['value']
        
        # 打印value中的键
        print(f"\nvalue中的键: {list(value.keys())}")
        
        # 检查是否包含dlt(大乐透)数据
        if 'dlt' in value and value['dlt']:
            dlt_data = value['dlt']
            print(f"\ndlt数据中的键: {list(dlt_data.keys())}")
            
            # 打印大乐透的基本信息
            print("\n大乐透基本信息:")
            for key in ['lotteryGameName', 'lotteryDrawNum', 'lotteryDrawTime', 'lotteryDrawResult']:
                if key in dlt_data:
                    print(f"  {key}: {dlt_data[key]}")
            
            # 打印奖池信息
            if 'poolInfo' in dlt_data:
                print("\n奖池信息:")
                for key, val in dlt_data['poolInfo'].items():
                    print(f"  {key}: {val}")
            
            # 打印奖级信息
            if 'awardList' in dlt_data:
                print(f"\n奖级信息(共{len(dlt_data['awardList'])}个奖级):")
                for award in dlt_data['awardList']:
                    print(f"  {award.get('prizeLevel', '未知奖级')}: 注数={award.get('stakeCount', '0')}, 奖金总额={award.get('totalPrizeamount', '0')}")
            
            # 打印期号列表
            if 'termList' in dlt_data:
                print(f"\n期号列表(共{len(dlt_data['termList'])}期): {dlt_data['termList'][:10]}...")

def run_tests():
    """运行所有测试用例"""
    print("=" * 60)
    print("数字彩票API接口测试(版本2)")
    print("=" * 60)
    
    # 测试用例1: 超级大乐透(85)最近一期, isVerify=1
    print("\n测试用例1: 超级大乐透(85)最近一期, isVerify=1")
    print("-" * 40)
    data1 = test_digital_lottery_api("85,0", 1)
    if data1:
        save_response_to_file(data1, "dlt_latest_verify_1.json")
        analyze_lottery_data(data1)
    
    # 测试用例2: 超级大乐透(85)最近一期, isVerify=0
    print("\n测试用例2: 超级大乐透(85)最近一期, isVerify=0")
    print("-" * 40)
    data2 = test_digital_lottery_api("85,0", 0)
    if data2:
        save_response_to_file(data2, "dlt_latest_verify_0.json")
        analyze_lottery_data(data2)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()