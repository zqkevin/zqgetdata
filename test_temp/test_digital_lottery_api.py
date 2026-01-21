#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字彩票API接口测试脚本
用于验证getDigitalDrawInfoV1.qry接口的参数要求
"""

import requests
import json

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

def print_response_data(data):
    """打印API响应数据的关键信息"""
    if data and 'errorCode' in data:
        print(f"错误码: {data['errorCode']}")
        print(f"错误信息: {data['errorMessage']}")
        
        if data['errorCode'] == '0' and 'value' in data:
            value = data['value']
            print("\n开奖信息:")
            for key, val in value.items():
                print(f"  {key}: {val}")
    else:
        print("无效的响应数据")

def run_tests():
    """运行所有测试用例"""
    print("=" * 60)
    print("数字彩票API接口测试")
    print("=" * 60)
    
    # 测试用例1: 超级大乐透(85)最近一期, isVerify=1
    print("\n测试用例1: 超级大乐透(85)最近一期, isVerify=1")
    print("-" * 40)
    data1 = test_digital_lottery_api("85,0", 1)
    print_response_data(data1)
    
    # 测试用例2: 超级大乐透(85)最近一期, isVerify=0
    print("\n测试用例2: 超级大乐透(85)最近一期, isVerify=0")
    print("-" * 40)
    data2 = test_digital_lottery_api("85,0", 0)
    print_response_data(data2)
    
    # 测试用例3: 超级大乐透(85)指定期号(模拟), isVerify=1
    print("\n测试用例3: 超级大乐透(85)指定期号(2025001), isVerify=1")
    print("-" * 40)
    data3 = test_digital_lottery_api("85,2025001", 1)
    print_response_data(data3)
    
    # 测试用例4: 排列3(pl3), 最近一期, isVerify=1
    print("\n测试用例4: 排列3(pl3), 最近一期, isVerify=1")
    print("-" * 40)
    data4 = test_digital_lottery_api("pl3,0", 1)
    print_response_data(data4)
    
    # 测试用例5: 错误的彩票类型代码(999), 最近一期, isVerify=1
    print("\n测试用例5: 错误的彩票类型代码(999), 最近一期, isVerify=1")
    print("-" * 40)
    data5 = test_digital_lottery_api("999,0", 1)
    print_response_data(data5)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()