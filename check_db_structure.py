# -*- coding: utf-8 -*-
"""
检查数据库表结构的脚本
"""

import pymysql

# 数据库连接信息 - 使用local配置
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'soccer_data',
    'password': 'pety93033',
    'database': 'soccer_data',
    'charset': 'utf8mb4'
}

try:
    # 连接数据库
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    print("=== 数据库表结构检查 ===")
    
    # 检查tczq_match表的字段
    print("\n1. tczq_match表的字段:")
    cursor.execute('SHOW COLUMNS FROM tczq_match')
    columns = cursor.fetchall()
    for column in columns:
        print(f"字段名: {column[0]}, 类型: {column[1]}, 是否为空: {column[2]}, 默认值: {column[4]}")
    
    # 检查tczq_match表的状态字段是否存在
    print("\n2. 检查status字段:")
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tczq_match' AND COLUMN_NAME LIKE '%status%'")
    status_columns = cursor.fetchall()
    if status_columns:
        print("找到的状态相关字段:")
        for col in status_columns:
            print(f"- {col[0]}")
    else:
        print("没有找到状态相关字段")
    
    # 检查tczq_match表的记录数
    print("\n3. tczq_match表的记录数:")
    cursor.execute('SELECT COUNT(*) FROM tczq_match')
    count = cursor.fetchone()[0]
    print(f"共有 {count} 条记录")
    
    # 如果有记录，查看前几条记录的基本信息（不包含status字段）
    if count > 0:
        print("\n4. tczq_match表的前2条记录:")
        cursor.execute('SELECT match_id, match_name FROM tczq_match LIMIT 2')
        records = cursor.fetchall()
        for record in records:
            print(f"比赛ID: {record[0]}, 比赛名称: {record[1]}")
    
    # 关闭游标和连接
    cursor.close()
    conn.close()
    
    print("\n=== 检查完成 ===")
    
except Exception as e:
    print(f"检查失败: {str(e)}")
    import traceback
    traceback.print_exc()