import pymysql
import json
import requests
from datetime import datetime
from config import config

# 连接数据库
db_config = config['local']
conn = pymysql.connect(
    host=db_config['host'],
    port=db_config['port'],
    user=db_config['user'],
    password=db_config['password'],
    database=db_config['database']
)
cursor = conn.cursor()

# 查询需要获取结果的第一场比赛
try:
    cursor.execute('''
        SELECT * FROM tczq_match 
        WHERE status = 0 
        AND CONCAT(match_date, ' ', match_time) < NOW() 
        ORDER BY match_date DESC, match_time DESC 
        LIMIT 1
    ''')
    match = cursor.fetchone()
    
    if match:
        match_id = match[0]
        match_week = match[2]
        match_num = match[3]
        home_team = match[4]
        away_team = match[5]
        match_date = match[6]
        match_time = match[7]
        
        print(f"查询到需要获取结果的比赛：")
        print(f"比赛ID: {match_id}")
        print(f"比赛周: {match_week}")
        print(f"比赛编号: {match_num}")
        print(f"主队: {home_team}")
        print(f"客队: {away_team}")
        print(f"比赛日期: {match_date}")
        print(f"比赛时间: {match_time}")
        
        # 测试API调用
        print("\n测试API调用...")
        
        # 创建会话
        session = requests.Session()
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.sporttery.cn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.sporttery.cn/',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        session.headers.update(headers)
        
        # 测试不同的API参数格式
        api_url = "https://webapi.sporttery.cn/gateway/uniform/football/getUniformMatchResultV1.qry"
        
        # 测试1: 使用当前日期
        current_date = datetime.now().strftime('%Y-%m-%d')
        params1 = {"channel": "c", "matchDate": current_date}
        
        print(f"\n测试1 - 使用当前日期 ({current_date}):")
        try:
            response1 = session.get(api_url, params=params1, timeout=30)
            print(f"状态码: {response1.status_code}")
            print(f"响应文本: {response1.text[:500]}...")
            
            if response1.status_code == 200:
                data1 = response1.json()
                print(f"错误码: {data1.get('errorCode')}")
                print(f"错误信息: {data1.get('errorMessage')}")
                print(f"成功标志: {data1.get('success')}")
        except Exception as e:
            print(f"请求失败: {str(e)}")
        
        # 测试2: 使用比赛日期
        params2 = {"channel": "c", "matchDate": match_date}
        
        print(f"\n测试2 - 使用比赛日期 ({match_date}):")
        try:
            response2 = session.get(api_url, params=params2, timeout=30)
            print(f"状态码: {response2.status_code}")
            print(f"响应文本: {response2.text[:500]}...")
            
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"错误码: {data2.get('errorCode')}")
                print(f"错误信息: {data2.get('errorMessage')}")
                print(f"成功标志: {data2.get('success')}")
        except Exception as e:
            print(f"请求失败: {str(e)}")
        
        # 测试3: 不使用matchDate参数
        params3 = {"channel": "c"}
        
        print(f"\n测试3 - 不使用matchDate参数:")
        try:
            response3 = session.get(api_url, params=params3, timeout=30)
            print(f"状态码: {response3.status_code}")
            print(f"响应文本: {response3.text[:500]}...")
            
            if response3.status_code == 200:
                data3 = response3.json()
                print(f"错误码: {data3.get('errorCode')}")
                print(f"错误信息: {data3.get('errorMessage')}")
                print(f"成功标志: {data3.get('success')}")
        except Exception as e:
            print(f"请求失败: {str(e)}")
        
    else:
        print("没有需要获取结果的比赛")
        
except Exception as e:
    print(f"查询数据库失败: {str(e)}")
finally:
    cursor.close()
    conn.close()