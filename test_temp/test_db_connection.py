#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库连接脚本
"""
import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from config import config
    from sqlalchemy import create_engine
    from app.database.tcbk_models import Base
    from app.database import localdb
    
    print("=== 数据库连接测试 ===")
    
    # 测试配置加载
    print("\n1. 测试配置加载:")
    db_config = config['local']
    print(f"配置: {db_config}")
    
    # 测试SQLAlchemy直接连接
    print("\n2. 测试SQLAlchemy直接连接:")
    try:
        engine = create_engine(
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        
        with engine.connect() as connection:
            print("✓ SQLAlchemy直接连接成功!")
            
            # 测试创建表
            print("\n3. 测试创建篮球表结构:")
            try:
                # 创建所有表
                Base.metadata.create_all(engine)
                print("✓ 篮球表结构创建成功!")
                
                # 打印创建的表
                print("\n4. 已创建的表:")
                for table_name in Base.metadata.tables.keys():
                    print(f"  - {table_name}")
                    
            except Exception as e:
                print(f"✗ 创建表结构失败: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"✗ SQLAlchemy直接连接失败: {e}")
        traceback.print_exc()
    
    # 测试使用localdb连接
    print("\n5. 测试使用localdb连接:")
    try:
        # 简单测试查询
        from app.database.tcbk_models import TcbkLeague
        result = localdb.query(TcbkLeague).first()
        print(f"✓ localdb连接成功! 查询结果: {result}")
    except Exception as e:
        print(f"✗ localdb连接失败: {e}")
        traceback.print_exc()
        
    print("\n=== 测试完成 ===")
    
except Exception as e:
    print(f"✗ 测试脚本执行失败: {e}")
    traceback.print_exc()