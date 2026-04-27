# -*- coding: utf-8 -*-
"""
初始化 soccer_server 数据库表
运行此脚本创建 API 服务所需的表结构
"""
import sys
import os

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_core import SelfDB
from database.server_models.user_models import Base as UserBase
from database.server_models.bet_models import Base as BetBase
from database.server_models.favorite_models import Base as FavoriteBase
from database.server_models.system_models import Base as SystemBase
from config import settings


def init_server_db():
    """初始化 API 服务数据库表"""
    print("=" * 60)
    print("  初始化 soccer_server 数据库")
    print("=" * 60)
    print()
    
    try:
        # 创建 SelfDB 实例
        db = SelfDB()
        
        # 创建所有表
        print(f"📊 连接到数据库: {settings.SERVER_DB_NAME}@{settings.SERVER_DB_HOST}:{settings.SERVER_DB_PORT}")
        print(f"👤 用户: {settings.SERVER_DB_USER}")
        print()
        
        # 使用 engine 创建所有表
        UserBase.metadata.create_all(db.engine)
        BetBase.metadata.create_all(db.engine)
        FavoriteBase.metadata.create_all(db.engine)
        SystemBase.metadata.create_all(db.engine)
        
        print("✅ 成功创建以下表:")
        print("  用户相关:")
        print("    - api_users (用户表)")
        print("    - user_level_config (等级配置表)")
        print("    - user_balance_logs (余额变动日志)")
        print("  投注相关:")
        print("    - bet_records (投注记录表)")
        print("    - bet_orders (投注订单表)")
        print("  收藏/关注相关:")
        print("    - user_favorites (用户收藏表)")
        print("    - user_follows (用户关注表)")
        print("  系统相关:")
        print("    - query_logs (查询日志表)")
        print("    - api_tokens (API Token 表)")
        print("    - system_config (系统配置表)")
        print()
        print("🎉 数据库初始化完成！")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_server_db()
    sys.exit(0 if success else 1)
