# -*- coding: utf-8 -*-
import os

# 从环境变量读取数据库配置，如果没有则使用默认值
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'soccer')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
DB_NAME = os.getenv('DB_NAME', 'soccer_data')

config = {
    'database': {
        'host': '172.18.0.4',
        'port': 3306,
        'user': 'soccer_data',
        'password': 'pety93033',
        'database': 'soccer_data'
    },
    'ubutun': {
        'host': '192.168.2.18',
        'port': 3306,
        'user': 'soccer_data',
        'password': 'pety93033',
        'database': 'soccer_data'
    },
    'local': {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'database': DB_NAME
    }
}