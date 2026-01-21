import json

import requests
from sqlalchemy import create_engine

def get_more_info(rolue='zq'):
    if rolue == 'zq':
        url = 'https://webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry?clientCode=3001'
    else:
        url = 'https://webapi.sporttery.cn/gateway/uniform/basketball/getMatchListV2.qry?clientCode=3001'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/80.0.3987.149 Safari/537.36',
        'Referer': 'https://www.sporttery.cn/',  # 参考真实页面
    }
    response = requests.get(url, headers=headers)
    match_list = {}
    if response.status_code == 200:
        response.encoding = 'utf-8'
        text_dict = json.loads(response.text)
        value = text_dict.get('value')
        day_matchs = value.get('matchInfoList')
        for day in day_matchs:
            for match in day.get('subMatchList'):
                if rolue == 'zq':
                    match_list[match.get('matchNum')] = match
                else:
                    match_list[match.get('matchNumStr')] = match
        return match_list
    else:
        return None

def test_get_vtools_config():
    """
    测试投注配置信息接口
    """
    url = 'https://webapi.sporttery.cn/gateway/report/getVtoolsConfigV1.qry?configKey=vtools:config:zc_app_loty_betshu'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/80.0.3987.149 Safari/537.36',
        'Referer': 'https://www.sporttery.cn/',
    }
    print("\n===== 测试投注配置信息接口 =====")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            response.encoding = 'utf-8'
            data = json.loads(response.text)
            print(f"请求成功: {data.get('success')}")
            print(f"错误信息: {data.get('errorMessage')}")
            
            # 打印部分关键配置信息
            if 'value' in data and 'zc_app_loty_betshu' in data['value']:
                config = data['value']['zc_app_loty_betshu'][0]
                print("\n主要玩法状态:")
                for game_type in ['jczq', 'jclq', 'r9', 'sfc']:
                    print(f"{game_type}: {config.get(game_type, 'N/A')}")
                
                print("\n主要玩法投注上限:")
                for game_type in ['jczq_max', 'jclq_max', 'r9_max', 'sfc_max']:
                    print(f"{game_type}: {config.get(game_type, 'N/A')}")
                
                print("\n部分金额限制信息:")
                if 'amountInfos' in config:
                    for key in ['jczq_offline', 'jclq_offline'][:1]:  # 只打印部分以避免输出过长
                        if key in config['amountInfos']:
                            info = config['amountInfos'][key]
                            print(f"{key}: 限制={info.get('amount_limit')}, 提示={info.get('amount_tips')}")
            return data
    except Exception as e:
        print(f"请求出错: {e}")
    return None

def test_get_match_calculator():
    """
    测试比赛计算器接口
    """
    url = 'https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry?poolCode=hhad,had&channel=c'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/80.0.3987.149 Safari/537.36',
        'Referer': 'https://www.sporttery.cn/',
    }
    print("\n===== 测试比赛计算器接口 =====")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            response.encoding = 'utf-8'
            data = json.loads(response.text)
            print(f"请求成功: {data.get('success')}")
            print(f"错误信息: {data.get('errorMessage')}")
            # 打印响应结构
            print(f"响应结构: {list(data.keys())}")
            if 'value' in data:
                print(f"value字段类型: {type(data['value'])}")
            return data
    except Exception as e:
        print(f"请求出错: {e}")
    return None

def test_search_odds(match_id="2035566"):
    """
    测试赔率搜索接口
    """
    url = f'https://webapi.sporttery.cn/gateway/uniform/football/searchOddsV1.qry?channel=c&type=&matchId={match_id}&single=0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/80.0.3987.149 Safari/537.36',
        'Referer': 'https://www.sporttery.cn/',
    }
    print("\n===== 测试赔率搜索接口 =====")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            response.encoding = 'utf-8'
            data = json.loads(response.text)
            print(f"请求成功: {data.get('success')}")
            print(f"错误信息: {data.get('errorMessage')}")
            # 打印响应结构
            print(f"响应结构: {list(data.keys())}")
            if 'value' in data:
                print(f"value字段类型: {type(data['value'])}")
                # 如果value是字典，打印键名
                if isinstance(data['value'], dict):
                    print(f"value字段键名: {list(data['value'].keys())}")
            return data
    except Exception as e:
        print(f"请求出错: {e}")
    return None

# 执行所有测试
def run_all_tests():
    print("开始测试 webapi.sporttery.cn API 接口")
    
    # 获取比赛列表（原有功能）
    print("\n===== 获取比赛列表 =====")
    match_list = get_more_info()
    if match_list:
        print(f"获取到 {len(match_list)} 场比赛")
        # 获取第一个比赛的ID用于测试其他接口
        first_match_id = list(match_list.keys())[0] if match_list else "2035566"
        print(f"第一个比赛ID: {first_match_id}")
    else:
        first_match_id = "2035566"
    
    # 测试其他接口
    config_data = test_get_vtools_config()
    calculator_data = test_get_match_calculator()
    # 使用实际比赛ID测试赔率接口
    odds_data = test_search_odds(first_match_id)
    
    print("\n===== 测试完成 =====")

# 主程序入口
if __name__ == "__main__":
    # 如果是直接运行此脚本，则执行所有测试
    run_all_tests()
else:
    # 保持原有功能
    match_list = get_more_info()
    print('debug')
    import pandas as pd
    df = pd.DataFrame(match_list).T
    oddslist = df['oddsList'].tolist()