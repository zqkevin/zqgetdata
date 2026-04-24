# -*- coding: utf-8 -*-
"""
重构后的数据库表结构初始化脚本
保留原有数据，创建新的表结构
"""
import sys
import os

# 添加项目根目录到 Python 路径（从 app/common/ 回到项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from config import config
from sqlalchemy import create_engine, inspect
from app.database.base_models import Base as BaseModels, League, Team, TeamAlias
from app.database import TczqMatch, BjdcMatch
# 导入 Base 类用于创建表
from app.database.tczq_models import Base as TczqBase
from app.database.bjdc_models import Base as BjdcBase

def check_table_exists(engine, table_name):
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def init_restructured_database():
    """
    初始化重构后的数据库表结构
    - 保留原有的 league 和 team 表 (公用)
    - 创建新的 tczq_ 和 bjdc_ 开头的独立表
    """
    # 使用 config 中配置的 db_type
    db_type = config.get('db_type', 'local')
    db_config = config[db_type]
    engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    print("=" * 60)
    print("=== 重构后的数据库表结构初始化 ===")
    print("=" * 60)
    
    try:
        # 1. 检查并保留原有表
        print("\n正在检查现有表结构...")
        existing_league = check_table_exists(engine, 'league')
        existing_team = check_table_exists(engine, 'team')
        existing_team_alias = check_table_exists(engine, 'team_alias')
        
        if existing_league:
            print("✓ 发现原有 league 表 (将保留)")
        else:
            print("✗ 未发现 league 表 (需要创建)")
            
        if existing_team:
            print("✓ 发现原有 team 表 (将保留)")
        else:
            print("✗ 未发现 team 表 (需要创建)")
            
        if existing_team_alias:
            print("✓ 发现原有 team_alias 表 (将保留)")
        else:
            print("✗ 未发现 team_alias 表 (需要创建)")
        
        # 2. 创建基础模型表 (如果不存在)
        print("\n=== 初始化基础数据表 (公用) ===")
        print("开始创建基础表结构...")
        BaseModels.metadata.create_all(engine)
        print("✓ 基础表结构创建完成!")
        
        # 3. 创建体彩足球表
        print("\n=== 初始化体彩足球 (TCZQ) 表结构 ===")
        print("开始创建体彩足球表结构...")
        tczq_tables_created = []
        for table in TczqBase.metadata.tables.values():
            if not check_table_exists(engine, table.name):
                table.create(bind=engine)
                tczq_tables_created.append(table.name)
        
        if tczq_tables_created:
            print("✓ 体彩足球表结构创建完成!")
            print("已创建的表:")
            for tbl in tczq_tables_created:
                print(f"  - {tbl}")
        else:
            print("✓ 体彩足球表已存在，无需创建")
        
        # 4. 创建北京单场表
        print("\n=== 初始化北京单场 (BJDC) 表结构 ===")
        print("开始创建北京单场表结构...")
        bjdc_tables_created = []
        for table in BjdcBase.metadata.tables.values():
            if not check_table_exists(engine, table.name):
                table.create(bind=engine)
                bjdc_tables_created.append(table.name)
        
        if bjdc_tables_created:
            print("✓ 北京单场表结构创建完成!")
            print("已创建的表:")
            for tbl in bjdc_tables_created:
                print(f"  - {tbl}")
        else:
            print("✓ 北京单场表已存在，无需创建")
        
        # 5. 显示最终的表结构
        print("\n=== 数据库表结构总览 ===")
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        print(f"\n数据库中共有 {len(all_tables)} 个表:")
        
        # 分类显示
        base_tables = [t for t in all_tables if t in ['league', 'team', 'team_alias']]
        tczq_tables = [t for t in all_tables if t.startswith('tczq_')]
        bjdc_tables = [t for t in all_tables if t.startswith('bjdc_')]
        other_tables = [t for t in all_tables if t not in base_tables + tczq_tables + bjdc_tables]
        
        if base_tables:
            print("\n📊 基础数据表 (公用):")
            for tbl in sorted(base_tables):
                print(f"  - {tbl}")
        
        if tczq_tables:
            print(f"\n⚽ 体彩足球表 ({len(tczq_tables)}个):")
            for tbl in sorted(tczq_tables):
                print(f"  - {tbl}")
        
        if bjdc_tables:
            print(f"\n🏆 北京单场表 ({len(bjdc_tables)}个):")
            for tbl in sorted(bjdc_tables):
                print(f"  - {tbl}")
        
        if other_tables:
            print(f"\n📋 其他表 ({len(other_tables)}个):")
            for tbl in sorted(other_tables):
                print(f"  - {tbl}")
        
        print("\n=== 数据库表结构初始化完成! ===")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_restructured_database()
    if success:
        print("\n✅ 所有操作完成!")
    else:
        print("\n❌ 操作失败，请检查错误信息")
