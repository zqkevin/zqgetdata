# -*- coding: utf-8 -*-
"""
数据库初始化整合脚本
用于创建所有彩票相关表结构并初始化必要数据
"""
import json
import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# 导入各个模块的Base类和模型
from app.database.digital_lottery_models import Base as DigitalBase
from app.database.tcbk_models import Base as TcbkBase
from app.database.tczq_models import Base as TczqBase, TczqLeague
from app.database.bjdc_models import Base as BjdcBase

# 联赛数据
with open('doc/leagues.json', 'r', encoding='utf-8') as f:
    LEAGUE_DATA = json.load(f)


def test_database_connection():
    """
    测试数据库连接
    
    Returns:
        bool: 连接成功返回True，否则返回False
    """
    try:
        # 获取数据库配置
        db_config = config['local']
        
        # 创建数据库引擎
        engine = create_engine(
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        
        print("正在测试数据库连接...")
        # 测试数据库连接
        with engine.connect() as connection:
            print("数据库连接成功!")
            return True
            
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


def get_engine():
    """
    获取数据库引擎
    
    Returns:
        engine: SQLAlchemy数据库引擎
    """
    db_config = config['local']
    return create_engine(
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )


def init_digital_lottery_database(engine):
    """
    初始化数字彩票数据库表结构
    """
    try:
        print("\n=== 初始化数字彩票表结构 ===")
        print("开始创建数字彩票表结构...")
        
        # 创建所有表
        DigitalBase.metadata.create_all(engine)
        
        print("表结构创建成功!")
        print("已创建的表:")
        for table_name in DigitalBase.metadata.tables.keys():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"初始化数字彩票数据库失败: {e}")
        traceback.print_exc()
        return False


def init_tcbk_database(engine):
    """
    初始化体彩篮球数据库表结构
    """
    try:
        print("\n=== 初始化体彩篮球表结构 ===")
        print("开始创建体彩篮球表结构...")
        
        # 创建所有表
        TcbkBase.metadata.create_all(engine)
        
        print("表结构创建成功!")
        print("已创建的表:")
        for table_name in TcbkBase.metadata.tables.keys():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"初始化体彩篮球数据库失败: {e}")
        traceback.print_exc()
        return False


def init_tczq_database(engine):
    """
    初始化体彩足球数据库表结构
    """
    try:
        print("\n=== 初始化体彩足球表结构 ===")
        print("开始创建体彩足球表结构...")
        # 创建所有表
        TczqBase.metadata.create_all(engine)
        
        print("表结构创建成功!")
        print("已创建的表:")
        for table_name in TczqBase.metadata.tables.keys():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"初始化体彩足球数据库失败: {e}")
        traceback.print_exc()
        return False


def init_bjdc_database(engine):
    """
    初始化北京单场数据库表结构
    """
    try:
        print("\n=== 初始化北京单场表结构 ===")
        print("开始创建北京单场表结构...")
        
        # 创建所有表
        BjdcBase.metadata.create_all(engine)
        
        print("表结构创建成功!")
        print("已创建的表:")
        for table_name in BjdcBase.metadata.tables.keys():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"初始化北京单场数据库失败: {e}")
        traceback.print_exc()
        return False


def init_league_data(engine):
    """
    初始化联赛数据
    """
    try:
        print("\n=== 初始化联赛数据 ===")
        print("导入联赛数据...")
        
        # 创建会话
        Session = sessionmaker(bind=engine)
        session = Session()
        
        for league_item in LEAGUE_DATA:
            league_id = int(league_item['leagueId'])
            league_name = league_item['leagueAllName']
            league_name_abbr = league_item['leagueAbbName']
            
            # 检查是否已存在
            existing_league = session.query(TczqLeague).filter_by(league_id=league_id).first()
            
            if existing_league:
                # 更新现有记录
                existing_league.league_name = league_name
                existing_league.league_name_abbr = league_name_abbr
                print(f"更新联赛: {league_name} ({league_name_abbr})")
            else:
                # 创建新记录
                new_league = TczqLeague(
                    league_id=league_id,
                    league_name=league_name,
                    league_name_abbr=league_name_abbr
                )
                session.add(new_league)
        print(f"添加联赛完成！")
        
        # 提交事务
        session.commit()
        session.close()
        
        print("联赛数据导入完成!")
        return True
        
    except Exception as e:
        print(f"初始化联赛数据失败: {e}")
        traceback.print_exc()
        return False


def init_all_databases():
    """
    初始化所有数据库表结构和数据
    """
    try:
        print("=== 数据库初始化整合脚本 ===")
        
        # 先测试数据库连接
        if not test_database_connection():
            print("请检查数据库配置后重试!")
            return False
        
        # 获取数据库引擎
        engine = get_engine()
        # 删除所有表格
        print("正在删除所有表格...")
        DigitalBase.metadata.drop_all(engine)
        TcbkBase.metadata.drop_all(engine)
        TczqBase.metadata.drop_all(engine)
        BjdcBase.metadata.drop_all(engine)
        print("删除所有表格完成！")
        # 初始化各个模块的数据库
        success = True
        
        if not init_digital_lottery_database(engine):
            success = False
        
        if not init_tcbk_database(engine):
            success = False
        
        if not init_tczq_database(engine):
            success = False
        
        if not init_bjdc_database(engine):
            success = False
        
        # 初始化联赛数据
        if not init_league_data(engine):
            success = False
        
        if success:
            print("\n=== 所有数据库初始化完成! ===")
        else:
            print("\n=== 部分数据库初始化失败，请查看错误信息 ===")
        
        return success
        
    except Exception as e:
        print(f"初始化过程中发生错误: {e}")
        traceback.print_exc()
        return False


def init_specific_module(module_name):
    """
    初始化特定模块的数据库
    
    Args:
        module_name: 模块名称 ('digital', 'tcbk', 'tczq', 'league')
    """
    try:
        print(f"=== 初始化{module_name}模块 ===")
        
        # 先测试数据库连接
        if not test_database_connection():
            print("请检查数据库配置后重试!")
            return False
        
        # 获取数据库引擎
        engine = get_engine()
        
        success = True
        
        if module_name == 'digital':
            success = init_digital_lottery_database(engine)
        elif module_name == 'tcbk':
            success = init_tcbk_database(engine)
        elif module_name == 'tczq':
            success = init_tczq_database(engine)
        elif module_name == 'bjdc':
            success = init_bjdc_database(engine)
        elif module_name == 'league':
            success = init_league_data(engine)
        else:
            print(f"未知模块: {module_name}")
            print("可用模块: digital, tcbk, tczq, bjdc, league")
            return False
        
        if success:
            print(f"\n=== {module_name}模块初始化完成! ===")
        else:
            print(f"\n=== {module_name}模块初始化失败，请查看错误信息 ===")
        
        return success
        
    except Exception as e:
        print(f"初始化过程中发生错误: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("数据库初始化整合脚本")
    print("使用说明:")
    print("1. 直接运行: 初始化所有数据库表结构和数据")
    print("2. 带参数运行: 初始化特定模块")
    print("   示例: python init_db.py digital")
    print("   可用模块: digital, tcbk, tczq, league")
    print()
    
    if len(sys.argv) == 1:
        # 初始化所有
        init_all_databases()
    elif len(sys.argv) == 2:
        # 初始化特定模块
        module_name = sys.argv[1].lower()
        init_specific_module(module_name)
    else:
        print("参数错误!")
        print("使用方法:")
        print("  python init_db.py [module_name]")
        print("  module_name: digital, tcbk, tczq, bjdc, league")