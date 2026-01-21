# -*- coding: utf-8 -*-
"""
查询爬虫程序是否成功记录了当前的赛事信息
主要检查tczq_match表中的记录情况
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pymysql
from config import config

def check_match_records():
    """
    检查tczq_match表中的记录情况
    """
    try:
        # 获取数据库配置
        db_config = config['local']
        
        # 连接数据库
        print("正在连接数据库...")
        conn = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4'
        )
        
        # 创建游标
        cursor = conn.cursor()
        
        # 查询tczq_match表中的记录数量
        print("\n=== 检查tczq_match表记录情况 ===")
        cursor.execute('SELECT COUNT(*) FROM tczq_match')
        total_count = cursor.fetchone()[0]
        print(f"tczq_match表中共有 {total_count} 条记录")
        
        # 查询最新的几条记录
        if total_count > 0:
            print(f"\n最新的 {min(5, total_count)} 条记录:")
            cursor.execute('SELECT match_id, match_name, match_date, match_time, status FROM tczq_match ORDER BY id DESC LIMIT 5')
            records = cursor.fetchall()
            
            # 打印记录
            for record in records:
                match_id, match_name, match_date, match_time, status = record
                status_text = {
                    0: "未开始",
                    1: "赛果已记录",
                    2: "赛果获取失败",
                    3: "比赛已取消",
                    4: "其他"
                }.get(status, "未知")
                
                print(f"比赛ID: {match_id}")
                print(f"  比赛名称: {match_name or '无'}")
                print(f"  比赛日期: {match_date or '无'}")
                print(f"  比赛时间: {match_time or '无'}")
                print(f"  状态: {status} ({status_text})")
                print("-" * 50)
        else:
            print("\ntczq_match表中没有记录")
        
        # 关闭游标和连接
        cursor.close()
        conn.close()
        
        return total_count
        
    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    check_match_records()