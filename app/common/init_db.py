# -*- coding: utf-8 -*-
"""
数据库初始化整合脚本
用于创建所有彩票相关表结构
注意：不再导入 JSON 文件预填充数据，联赛和球队数据通过实际采集动态补充
"""
import sys
import os
import traceback

# 添加项目根目录到Python路径（从 app/common/ 回到项目根目录）
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# 导入各个模块的 Base 类和模型
from app.database import DigitalLotteryDraw, TcbkMatch, League, Team
# 导入 Base 类用于创建表
from app.database.digital_lottery_models import Base as DigitalBase
from app.database.tcbk_models import Base as TcbkBase
from app.database.base_models import Base as FbBase


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
    初始化足球数据库表结构
    """
    try:
        print("\n=== 初始化足球表结构 ===")
        print("开始创建体彩足球表结构...")
        # 创建所有表
        FbBase.metadata.create_all(engine)
        
        print("表结构创建成功!")
        print("已创建的表:")
        for table_name in FbBase.metadata.tables.keys():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"初始化体彩足球数据库失败: {e}")
        traceback.print_exc()
        return False



def init_all_databases():
    """
    初始化所有数据库表结构（不导入JSON数据）
    联赛和球队数据通过实际采集时动态补充
    """
    try:
        print("=== 数据库初始化整合脚本 ===")
        print("注意：仅创建表结构，不导入预置数据")
        print("联赛和球队数据将在采集新赛事时自动补充\n")
        
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
        FbBase.metadata.drop_all(engine)
        print("删除所有表格完成！")
        # 初始化各个模块的数据库
        success = True
        
        if not init_digital_lottery_database(engine):
            success = False
        
        if not init_tcbk_database(engine):
            success = False
        
        if not init_tczq_database(engine):
            success = False
        
        if success:
            print("\n=== 所有数据库表结构创建完成! ===")
            print("提示：联赛和球队数据将在首次采集时自动创建")
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
        module_name: 模块名称 ('digital', 'tcbk', 'tczq')
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
        else:
            print(f"未知模块: {module_name}")
            print("可用模块: digital, tcbk, tczq")
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
    print("1. 直接运行: 初始化所有数据库表结构（不导入JSON数据）")
    print("2. 带参数运行: 初始化特定模块")
    print("   示例: python init_db.py digital")
    print("   可用模块: digital, tcbk, tczq")
    print()
    print("注意：联赛和球队数据将在首次采集时自动创建，无需预导入")
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
        print("  module_name: digital, tcbk, tczq")